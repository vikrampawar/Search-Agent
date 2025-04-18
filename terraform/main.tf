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

# Get latest Amazon Linux 2023 AMI if ami_id is not specified
# (Replaces the old Amazon Linux 2 default)
data "aws_ami" "amazon_linux_2023" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
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

# IAM role for EC2 to access ECR
resource "aws_iam_role" "ec2_ecr_role" {
  name = "search-agent-ec2-ecr-role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "ecr_readonly" {
  role       = aws_iam_role.ec2_ecr_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
}

resource "aws_iam_instance_profile" "ec2_ecr_profile" {
  name = "search-agent-ec2-ecr-profile"
  role = aws_iam_role.ec2_ecr_role.name
}

# Create an EC2 instance
resource "aws_instance" "app_server" {
  ami                    = var.ami_id == "" ? data.aws_ami.amazon_linux_2023.id : var.ami_id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.instance_sg.id]
  subnet_id              = var.subnet_id == "" ? data.aws_subnets.public.ids[0] : var.subnet_id
  user_data              = var.user_data_script
  iam_instance_profile   = aws_iam_instance_profile.ec2_ecr_profile.name

  root_block_device {
    volume_size = 32 # Increase as needed (in GB)
    volume_type = "gp2"
  }

  tags = merge(
    var.tags,
    {
      Name = var.app_name
    }
  )
}