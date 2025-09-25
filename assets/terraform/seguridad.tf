# Security Group para instancias  
resource "aws_security_group" "instances" {
  name_prefix = "instances-sg-"
  vpc_id      = aws_vpc.main.id

  # SSH restringido  
  ingress {
    description = "SSH from corporate"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.corporate_ip]
  }

  # HTTP desde ALB
  ingress {
    description     = "HTTP from ALB"
    from_port       = 80
    to_port         = 80
    protocol        = "tcp"
    security_groups = [aws_security_group.lb.id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  lifecycle {
    create_before_destroy = true
  }
}

# Security Group para VPN  
resource "aws_security_group" "vpn" {
  name_prefix = "vpn-sg-"
  vpc_id      = aws_vpc.main.id

  ingress {
    description = "IPSec"
    from_port   = 500
    to_port     = 500
    protocol    = "udp"
    cidr_blocks = [var.corporate_ip]
  }

  ingress {
    description = "IPSec NAT-T"
    from_port   = 4500
    to_port     = 4500
    protocol    = "udp"
    cidr_blocks = [var.corporate_ip]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Security Group para ALB
resource "aws_security_group" "lb" {
  name_prefix = "lb-sg-"
  vpc_id      = aws_vpc.main.id

  # HTTP público  
  ingress {
    description = "HTTP public"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    security_groups = [aws_security_group.instances.id]
  }
}