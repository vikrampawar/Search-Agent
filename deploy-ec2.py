#!/usr/bin/env python3

import os
import sys
import subprocess
import getpass
import stat

def run_command(command, shell=False):
    """Run a command and return its output"""
    try:
        if shell:
            result = subprocess.run(command, shell=True, check=True, text=True, stdout=subprocess.PIPE)
        else:
            result = subprocess.run(command, check=True, text=True, stdout=subprocess.PIPE)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        sys.exit(1)

def main():
    print("====== Search Agent AWS EC2 Deployment Script ======")
    print("")
    print("This script will help deploy your Search Agent to an AWS EC2 instance.")
    print("Make sure you've already launched an EC2 instance and have the following:")
    print("  - EC2 instance public DNS name")
    print("  - SSH key (.pem file)")
    print("  - Your Google API Key")
    print("")
    
    # Get user input
    ec2_dns = input("Enter your EC2 instance public DNS (e.g. ec2-1-2-3-4.compute-1.amazonaws.com): ")
    ssh_key = input("Enter the path to your SSH key (.pem file): ")
    google_api_key = getpass.getpass("Enter your Google API Key: ")  # For security, use getpass
    app_port = input("Enter the port for your application (default: 8010): ") or "8010"
    
    print("\nSetting up deployment...\n")
    
    # Create a temporary .env file with the API key
    with open("app/.env.deploy", "w") as env_file:
        env_file.write(f"GOOGLE_API_KEY={google_api_key}")
    
    # Ensure SSH key has correct permissions (400 - read by owner only)
    os.chmod(ssh_key, stat.S_IRUSR)
    
    print("===== Connecting to EC2 and setting up the environment =====")
    
    # Copy the project to the EC2 instance
    print("Copying project files to EC2...")
    run_command([
        "scp", "-i", ssh_key, "-r", 
        "./app", "./requirements.txt", 
        f"ubuntu@{ec2_dns}:~/Search-Agent/"
    ])
    
    # Run setup commands on the EC2 instance
    print("Setting up the environment on EC2...")
    
    # Prepare the main setup script
    setup_script = f"""
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
server {{
    listen 80;
    server_name {ec2_dns};
    
    location / {{
        proxy_pass http://localhost:{app_port};
        proxy_http_version 1.1;
        proxy_set_header Upgrade \\$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host \\$host;
        proxy_cache_bypass \\$http_upgrade;
    }}
}}
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
ExecStart=/home/ubuntu/Search-Agent/.venv/bin/uvicorn main:app --host 0.0.0.0 --port {app_port}

[Install]
WantedBy=multi-user.target
EOS'
    
    # Start and enable the service
    sudo systemctl daemon-reload
    sudo systemctl start search-agent
    sudo systemctl enable search-agent
    
    echo "Deployment completed successfully!"
    """
    
    # Execute setup script on the remote server
    run_command(["ssh", "-i", ssh_key, f"ubuntu@{ec2_dns}", setup_script])
    
    # Clean up
    os.remove("app/.env.deploy")
    
    print("\n====== Deployment Completed ======")
    print("")
    print(f"Your Search Agent should now be accessible at: http://{ec2_dns}")
    print("")
    print("To check the status of your application:")
    print(f'ssh -i "{ssh_key}" ubuntu@"{ec2_dns}" \'sudo systemctl status search-agent\'')
    print("")
    print("To view application logs:")
    print(f'ssh -i "{ssh_key}" ubuntu@"{ec2_dns}" \'sudo journalctl -u search-agent -f\'')
    print("")

if __name__ == "__main__":
    main()