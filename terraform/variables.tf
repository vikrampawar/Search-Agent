variable "region" {
  description = "AWS region to deploy resources"
  type        = string
  default     = "us-west-2"  # Default region, can override with terraform.tfvars
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t2.micro"
}

variable "ami_id" {
  description = "AMI ID for the EC2 instance (default is Amazon Linux 2)"
  type        = string
  default     = ""  # Leave empty to use the data source lookup
}

variable "key_name" {
  description = "Name of the SSH key pair to use"
  type        = string
  default     = ""  # Set in terraform.tfvars or through CLI
}

variable "vpc_id" {
  description = "VPC ID where resources should be created (defaults to default VPC if empty)"
  type        = string
  default     = ""
}

variable "subnet_id" {
  description = "Subnet ID where the EC2 instance should be deployed (defaults to first public subnet if empty)"
  type        = string
  default     = ""
}

variable "app_name" {
  description = "Name of the application"
  type        = string
  default     = "search-agent"
}

variable "open_ports" {
  description = "List of ports to open in the security group"
  type        = list(number)
  default     = [22, 80, 443, 5000]  # SSH, HTTP, HTTPS, Flask default
}

variable "user_data_script" {
  description = "User data script to execute on instance launch"
  type        = string
  default     = <<-EOF
    #!/bin/bash
    sudo yum update -y
    sudo yum install -y python3 python3-pip git docker
    sudo pip3 install flask requests
    sudo service docker start
    sudo usermod -a -G docker ec2-user
    # Log out and log back in for group changes to take effect (manual step if needed)
  EOF
}

variable "tags" {
  description = "Tags to apply to all resources"
  type        = map(string)
  default = {
    Environment = "development"
    Project     = "search-agent"
  }
}