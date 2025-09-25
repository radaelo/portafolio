# VPC Core
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true
  tags = {
    Name = "corporate-vpc"
  }
}

# Subnets Públicas
resource "aws_subnet" "public" {
  count = 2

  vpc_id                  = aws_vpc.main.id
  cidr_block              = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
  availability_zone       = count.index == 0 ? "${var.region}a" : "${var.region}b"
  map_public_ip_on_launch = true
  tags = {
    Name = "public-subnet-${count.index + 1}"
    Tier = "public"
  }
}

# Internet Gateway
resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "main-igw"
  }
}

# Tabla de Rutas Principal
resource "aws_route_table" "main" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }

  # Rutas corporativas a través del VPN
  dynamic "route" {
    for_each = setunion(toset(var.corporate_cidrs), toset([var.corporate_ip]))
    content {
      cidr_block = route.value
      gateway_id = aws_vpn_gateway.corp.id
    }
  }

  tags = {
    Name = "main-rt"
  }
}

# Asociación de Subnets
resource "aws_route_table_association" "public" {
  count = length(aws_subnet.public)

  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.main.id
}

# VPN Gateway
resource "aws_vpn_gateway" "corp" {
  vpc_id = aws_vpc.main.id
  tags = {
    Name = "corp-vpn-gw"
  }
}

# Elastic IP para VPN
resource "aws_eip" "vpn" {
  domain = "vpc"
  tags = {
    Name = "vpn-gw-ip"
  }
}

# Asociación de EIP
resource "aws_eip_association" "vpn" {
  allocation_id   = aws_eip.vpn.id
  vpn_gateway_id  = aws_vpn_gateway.corp.id
}	