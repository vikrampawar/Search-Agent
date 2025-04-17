terraform {
  required_version = ">= 1.0.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# Get latest Amazon Linux 2 AMI if ami_id is not specified
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# Get the default VPC if vpc_id is not specified
data "aws_vpc" "selected" {
  default = var.vpc_id == "" ? true : false
  id      = var.vpc_id == "" ? null : var.vpc_id
}

# Get public subnets if subnet_id is not provided
data "aws_subnets" "public" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.selected.id]
  }

  filter {
    name   = "map-public-ip-on-launch"
    values = [true]
  }
}

# Create a security group for our instance
resource "aws_security_group" "instance_sg" {
  name        = "${var.app_name}-sg"
  description = "Security group for ${var.app_name} EC2 instance"
  vpc_id      = data.aws_vpc.selected.id

  # Dynamic block to create ingress rules for all specified ports
  dynamic "ingress" {
    for_each = toset(var.open_ports)
    content {
      from_port   = ingress.value
      to_port     = ingress.value
      protocol    = "tcp"
      cidr_blocks = ["0.0.0.0/0"]
      description = "Allow ${ingress.value}"
    }
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "Allow all outbound traffic"
  }

  tags = merge(
    var.tags,
    {
      Name = "${var.app_name}-sg"
    }
  )
}

# Create an EC2 instance
resource "aws_instance" "app_server" {
  ami                    = var.ami_id == "" ? data.aws_ami.amazon_linux_2.id : var.ami_id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.instance_sg.id]
  subnet_id              = var.subnet_id == "" ? data.aws_subnets.public.ids[0] : var.subnet_id
  user_data              = var.user_data_script

  tags = merge(
    var.tags,
    {
      Name = var.app_name
    }
  )
}