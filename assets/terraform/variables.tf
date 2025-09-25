variable "region" {
  description = "AWS region"
  default     = "us-east-1"
}

variable "corporate_gateway_ip" {
  description = "IP pública del gateway corporativo"
  default     = "198.19.18.11"
}

variable "corporate_cidrs" {
  description = "CIDRs de la red corporativa"
  type        = list(string)
  default     = ["172.16.0.0/24", "172.16.1.0/24", "172.16.2.0/24"]
}

variable "corporate_ip" {
  description = "CIDR de acceso SSH corporativo"
  default     = "192.168.0.0/16"
}

variable "instance_type" {
  description = "Tipo de instancia EC2"
  default     = "t3.micro"
}

variable "vpn_psk_tunnel1" {
  description = "Clave precompartida para túnel VPN 1"
  sensitive   = true
}

variable "vpn_psk_tunnel2" {
  description = "Clave precompartida para túnel VPN 2"
  sensitive   = true
}