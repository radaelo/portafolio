# VPC Endpoints
resource "aws_vpc_endpoint" "s3" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.region}.s3"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.main.id]
}

resource "aws_vpc_endpoint" "dynamodb" {
  vpc_id            = aws_vpc.main.id
  service_name      = "com.amazonaws.${var.region}.dynamodb"
  vpc_endpoint_type = "Gateway"
  route_table_ids   = [aws_route_table.main.id]
}

# Customer Gateway
resource "aws_customer_gateway" "corp" {
  bgp_asn    = 65000
  ip_address = var.corporate_gateway_ip
  type       = "ipsec.1"
  tags = {
    Name = "corporate-gw"
  }
}

# VPN Connection
resource "aws_vpn_connection" "corp" {
  customer_gateway_id = aws_customer_gateway.corp.id
  vpn_gateway_id      = aws_vpn_gateway.corp.id
  type                = "ipsec.1"
  static_routes_only  = true

  tunnel1_inside_cidr   = "169.254.100.0/30"
  tunnel1_preshared_key = var.vpn_psk_tunnel1
  tunnel2_inside_cidr   = "169.254.200.0/30"
  tunnel2_preshared_key = var.vpn_psk_tunnel2

  tags = {
    Name = "corp-vpn-connection"
  }

  # Rutas estáticas corporativas
  dynamic "static_routes" {
    for_each = var.corporate_cidrs
    content {
      destination_cidr_block = static_routes.value
    }
  }
}

# CloudFront Distribution
resource "aws_cloudfront_distribution" "app" {
  enabled             = true
  wait_for_deployment = false

  origin {
    domain_name = aws_lb.app_lb.dns_name
    origin_id   = "alb-origin"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  default_cache_behavior {
    target_origin_id       = "alb-origin"
    viewer_protocol_policy = "redirect-to-https"
    allowed_methods        = ["GET", "HEAD", "OPTIONS"]
    cached_methods         = ["GET", "HEAD"]

    forwarded_values {
      query_string = false
      headers      = ["Host"]
      cookies {
        forward = "none"
      }
    }

    min_ttl     = 0
    default_ttl = 3600
    max_ttl     = 86400
    compress    = true
  }

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = {
    Name = "app-distribution"
  }
}

# Application Load Balancer
resource "aws_lb" "app_lb" {
  name               = "app-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.lb.id]
  subnets            = aws_subnet.public[*].id

  tags = {
    Name = "app-load-balancer"
  }
}

# Target Group for Load Balancer
resource "aws_lb_target_group" "app" {
  name     = "app-tg"
  port     = 80
  protocol = "HTTP"
  vpc_id   = aws_vpc.main.id

  health_check {
    path                = "/"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
    matcher             = "200"
  }
}

# Load Balancer Listener
resource "aws_lb_listener" "front_end" {
  load_balancer_arn = aws_lb.app_lb.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}

# Target Group Attachments
resource "aws_lb_target_group_attachment" "app" {
  count = length(aws_instance.app)

  target_group_arn = aws_lb_target_group.app.arn
  target_id        = aws_instance.app[count.index].id
  port             = 80
}