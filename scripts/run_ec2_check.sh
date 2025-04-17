#!/bin/bash

# Helper script to deploy and run the EC2 checker script remotely
# Usage: ./run_ec2_check.sh <path-to-key> <ec2-instance-address>

if [ $# -lt 2 ]; then
    echo "Usage: $0 <path-to-key-file> <ec2-instance-address>"
    echo "Example: $0 ~/keys/vikramitwork-ec2-001-rsa.pem ec2-user@35.176.72.243"
    exit 1
fi

KEY_FILE="$1"
EC2_HOST="$2"

echo "===== Deploying EC2 Quick Check script to ${EC2_HOST} ====="

# Check if key file exists
if [ ! -f "$KEY_FILE" ]; then
    echo "Error: Key file $KEY_FILE not found!"
    exit 1
fi

# Ensure key has correct permissions
chmod 400 "$KEY_FILE"

# Copy the script to the server
echo "Copying script to EC2..."
scp -i "$KEY_FILE" "$(dirname "$0")/ec2_quick_check.py" "${EC2_HOST}:~/ec2_quick_check.py"

if [ $? -ne 0 ]; then
    echo "Error copying file to EC2 instance!"
    exit 1
fi

# Connect and run the script
echo -e "\n===== Running EC2 Quick Check on remote instance ====="
ssh -i "$KEY_FILE" "$EC2_HOST" "chmod +x ~/ec2_quick_check.py && python3 ~/ec2_quick_check.py"

echo -e "\n===== Check complete! ====="