output "vpc_id" {
  description = "ID de la VPC"
  value       = aws_vpc.main.id
}

output "cloudfront_url" {
  description = "URL de distribución CloudFront"
  value       = aws_cloudfront_distribution.app.domain_name
}

output "vpn_gateway_ip" {
  description = "IP pública del VPN Gateway"
  value       = aws_eip.vpn.public_ip
}

output "instance_public_ips" {
  description = "IPs públicas de las instancias"
  value = {
    for i, instance in aws_instance.app :
    instance.tags.Name => instance.public_ip
  }
}

output "vpn_connection_status" {
  description = "Estado de la conexión VPN"
  value       = aws_vpn_connection.corp.tunnel1_address
}

output "load_balancer_dns" {
  description = "DNS del Load Balancer"
  value       = aws_lb.app_lb.dns_name
}