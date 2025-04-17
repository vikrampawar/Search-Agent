#!/bin/bash

# Exit on error
set -e

echo "====== Search Agent AWS EC2 Deployment Script ======"
echo ""
echo "This script will help deploy your Search Agent to an AWS EC2 instance."
echo "Make sure you've already launched an EC2 instance and have the following:"
echo "  - EC2 instance public DNS name"
echo "  - SSH key (.pem file)"
echo "  - Your Google API Key"
echo ""

# Get user input
read -p "Enter your EC2 instance public DNS (e.g. ec2-1-2-3-4.compute-1.amazonaws.com): " EC2_DNS
read -p "Enter the path to your SSH key (.pem file): " SSH_KEY
read -p "Enter your Google API Key: " GOOGLE_API_KEY
read -p "Enter the port for your application (default: 8010): " APP_PORT
APP_PORT=${APP_PORT:-8010}

echo ""
echo "Setting up deployment..."
echo ""

# Create a temporary .env file with the API key
echo "GOOGLE_API_KEY=$GOOGLE_API_KEY" > app/.env.deploy

# Ensure SSH key has correct permissions
chmod 400 "$SSH_KEY"

# Deploy the application
echo "===== Connecting to EC2 and setting up the environment ====="

# Copy the project to the EC2 instance
echo "Copying project files to EC2..."
scp -i "$SSH_KEY" -r ./app ./requirements.txt ubuntu@"$EC2_DNS":~/Search-Agent/

# Run setup commands on the EC2 instance
echo "Setting up the environment on EC2..."
ssh -i "$SSH_KEY" ubuntu@"$EC2_DNS" << EOF
    # Update and install dependencies
    sudo apt update
    sudo apt install -y python3 python3-pip python3-venv nginx

    # Set up the application
    cd ~/Search-Agent
    python3 -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt

    # Configure Nginx
    sudo bash -c 'cat > /etc/nginx/sites-available/search-agent << EON
server {
    listen 80;
    server_name $EC2_DNS;

    location / {
        proxy_pass http://localhost:$APP_PORT;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
    }
}
EON'

    # Enable the site
    sudo ln -sf /etc/nginx/sites-available/search-agent /etc/nginx/sites-enabled/
    sudo nginx -t && sudo systemctl restart nginx

    # Set up systemd service
    sudo bash -c 'cat > /etc/systemd/system/search-agent.service << EOS
[Unit]
Description=Search Agent with Google ADK
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/Search-Agent/app
Environment="PATH=/home/ubuntu/Search-Agent/.venv/bin"
ExecStart=/home/ubuntu/Search-Agent/.venv/bin/uvicorn main:app --host 0.0.0.0 --port $APP_PORT

[Install]
WantedBy=multi-user.target
EOS'

    # Start and enable the service
    sudo systemctl daemon-reload
    sudo systemctl start search-agent
    sudo systemctl enable search-agent

    echo "Deployment completed successfully!"
EOF

# Clean up
rm app/.env.deploy

echo ""
echo "====== Deployment Completed ======"
echo ""
echo "Your Search Agent should now be accessible at: http://$EC2_DNS"
echo ""
echo "To check the status of your application:"
echo "ssh -i \"$SSH_KEY\" ubuntu@\"$EC2_DNS\" 'sudo systemctl status search-agent'"
echo ""
echo "To view application logs:"
echo "ssh -i \"$SSH_KEY\" ubuntu@\"$EC2_DNS\" 'sudo journalctl -u search-agent -f'"
echo ""