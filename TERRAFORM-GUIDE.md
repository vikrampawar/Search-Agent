# Terraform Deployment Guide for Search Agent

This guide explains how to deploy the Search Agent application to AWS using Terraform.

## Prerequisites

- [Terraform](https://www.terraform.io/downloads) installed (version 1.0.0+)
- AWS CLI configured with appropriate credentials
- An SSH key pair in your AWS account

## Quick Start

```bash
cd terraform
terraform init
terraform apply
```

## Configuration Files

The Terraform configuration includes:

- `main.tf` - Core infrastructure configuration
- `variables.tf` - Variable definitions
- `outputs.tf` - Output values after deployment
- `terraform.tfvars` - Variable values (customize this file)

## Customizing Your Deployment

Edit `terraform.tfvars` to customize your deployment:

```hcl
region        = "eu-west-2"    # AWS region
instance_type = "t2.micro"     # EC2 instance type
app_name      = "search-agent" # Name for resources
key_name      = "your-key-name" # Your SSH key name (without .pem)
```

## What Gets Deployed

- An EC2 instance running Amazon Linux
- Security group with ports 22 (SSH), 80 (HTTP), 443 (HTTPS), and 8010 (App)
- Nginx as a reverse proxy
- Your Search Agent application with a systemd service

## Post-Deployment Steps

After deployment completes:

1. SSH into your instance:
   ```bash
   ssh -i /path/to/your-key.pem ec2-user@<instance-ip>
   ```

2. Set your Google API key:
   ```bash
   vi /home/ec2-user/Search-Agent/app/.env
   # Replace "your-api-key-here" with your actual API key
   ```

3. Restart the application:
   ```bash
   sudo systemctl restart search-agent
   ```

## Troubleshooting

If you encounter issues:

1. Run the diagnostic script:
   ```bash
   /home/ec2-user/debug_search_agent.sh
   ```

2. Check if the virtual environment was created properly:
   ```bash
   ls -la /home/ec2-user/Search-Agent/.venv/bin
   ```

3. If needed, run the fix script:
   ```bash
   /home/ec2-user/fix_search_agent.sh
   ```

## Common Operations

### Destroying Infrastructure

```bash
terraform destroy
```

### Applying Changes

After modifying any Terraform files:

```bash
terraform apply
```

### Checking State

```bash
terraform show
```

## Security Considerations

- The `.env` file containing your API key is created on the server; you need to manually add your key
- Default security group rules allow minimum required access
- SSH key authentication is used for EC2 access

## Best Practices

1. Keep terraform.tfstate files out of version control (already in .gitignore)
2. Use Terraform workspaces for multiple environments
3. Consider using remote state (S3 + DynamoDB) for team environments
4. Review security group rules regularly

## Common Errors and Solutions

| Error | Solution |
|-------|----------|
| "No EC2 instance found with IP" | Check the correct region is set in AWS CLI |
| "Key pair not found" | Ensure the key_name matches exactly (no .pem extension) |
| "502 Bad Gateway" | Run debug_search_agent.sh and check logs |
| Missing API key | Set your API key in `/home/ec2-user/Search-Agent/app/.env` |