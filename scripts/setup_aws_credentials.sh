#!/bin/bash
# Script to help set up AWS credentials for EC2 management
# This will configure your AWS credentials specifically for managing EC2 instances

# Colors for output
GREEN="\033[0;32m"
YELLOW="\033[0;33m"
BLUE="\033[0;34m"
NC="\033[0m" # No Color

# Print header
echo -e "${BLUE}=================================${NC}"
echo -e "${BLUE}AWS Credentials Setup for EC2${NC}"
echo -e "${BLUE}=================================${NC}"
echo ""
echo "This script will help you set up AWS credentials needed to manage EC2 instances."
echo "You'll need your AWS Access Key ID and Secret Access Key ready."
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo -e "${YELLOW}AWS CLI not found. Installing...${NC}"
    pip install awscli
fi

# Create AWS config directory if it doesn't exist
mkdir -p ~/.aws

# Prompt for credentials
echo -e "${BLUE}Please enter your AWS credentials:${NC}"
read -p "AWS Access Key ID: " AWS_ACCESS_KEY_ID
read -p "AWS Secret Access Key: " AWS_SECRET_ACCESS_KEY
read -p "Default region name [us-east-1]: " AWS_REGION
AWS_REGION=${AWS_REGION:-us-east-1}
read -p "Default output format [json]: " AWS_OUTPUT
AWS_OUTPUT=${AWS_OUTPUT:-json}

# Write to credentials file
echo -e "${YELLOW}Writing credentials to ~/.aws/credentials...${NC}"
cat >> ~/.aws/credentials << EOF
[default]
aws_access_key_id = $AWS_ACCESS_KEY_ID
aws_secret_access_key = $AWS_SECRET_ACCESS_KEY
EOF

# Write to config file
echo -e "${YELLOW}Writing configuration to ~/.aws/config...${NC}"
cat >> ~/.aws/config << EOF
[default]
region = $AWS_REGION
output = $AWS_OUTPUT
EOF

# Set permissions
chmod 600 ~/.aws/credentials
chmod 600 ~/.aws/config

echo ""
echo -e "${GREEN}AWS credentials have been configured successfully!${NC}"
echo ""

# Test the configuration
echo -e "${YELLOW}Testing your credentials...${NC}"
if aws sts get-caller-identity &> /dev/null; then
    echo -e "${GREEN}Authentication successful! Your credentials are working.${NC}"
    
    # Test EC2 permissions
    echo -e "${YELLOW}Testing EC2 permissions...${NC}"
    if aws ec2 describe-regions --region $AWS_REGION &> /dev/null; then
        echo -e "${GREEN}EC2 permissions confirmed! You can now manage EC2 instances.${NC}"
    else
        echo -e "${YELLOW}Warning: Your AWS user doesn't have EC2 permissions.${NC}"
        echo "You'll need to ask your AWS administrator to grant your user the necessary EC2 permissions."
        echo "At minimum, you need: ec2:DescribeInstances, ec2:DescribeSecurityGroups, ec2:AuthorizeSecurityGroupIngress"
    fi
else
    echo -e "${YELLOW}Authentication failed. Please check your credentials and try again.${NC}"
fi

echo ""
echo "Now you can run the EC2 port opening script:"
echo "./scripts/open_http_port.sh 35.176.72.243"