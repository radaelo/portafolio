# AMI más reciente de Amazon Linux 2
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# Instancias
resource "aws_instance" "app" {
  count = 3

  ami           = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type

  subnet_id = element(aws_subnet.public.*.id, count.index < 2 ? 0 : 1)
  
  # IPs válidas dentro del rango de subred
  private_ip = cidrhost(
    aws_subnet.public[count.index < 2 ? 0 : 1].cidr_block, 
    count.index < 2 ? 10 + count.index : 10
  )

  vpc_security_group_ids = [aws_security_group.instances.id]

  user_data = <<-EOT
    #!/bin/bash
    yum install -y httpd
    systemctl start httpd
    systemctl enable httpd
    echo "<h1>Instance $((${count.index} + 1))</h1>" > /var/www/html/index.html
  EOT

  tags = {
    Name = "app-instance-${count.index + 1}"
  }

  lifecycle {
    ignore_changes = [ami]
  }
}