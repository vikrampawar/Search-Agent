# AWS EC2 Deployment Notes

This document contains additional information, learnings, and troubleshooting tips for deploying the Search Agent application to AWS EC2.

## Amazon Linux Versions

Amazon Linux comes in multiple versions:

### Amazon Linux 2023
- Latest version (end of support: June 30, 2029)
- Uses `yum` as package manager
- Install Nginx directly: `sudo yum install -y nginx`
- Uses systemd for service management
- Configuration directory: `/etc/nginx/conf.d/`

### Amazon Linux 2
- Previous version (end of support: June 30, 2025)
- Uses `yum` as package manager
- Install Nginx using extras: `sudo amazon-linux-extras install nginx1 -y`
- Uses systemd for service management
- Configuration directory: `/etc/nginx/conf.d/`

### How to Check Your Amazon Linux Version
Connect to your EC2 instance with SSH and run one of these commands:
```bash
# Most straightforward method
cat /etc/os-release

# Alternative methods
cat /etc/system-release
uname -r  # Kernel version (AL2023 typically uses 6.x)
```

## Reverse Proxy Explained

A reverse proxy is a server that sits between client devices (web browsers) and a web server (your application). It offers several benefits:

### What it does
- Receives client requests and forwards them to your backend application
- Returns responses from the application back to clients
- Controls and secures access to your application

### Benefits
1. **Port Standardization**: Clients connect to standard web ports (80/443) while your application runs on any port (8010)
2. **Security**: Creates an abstraction layer that protects your backend from direct exposure
3. **SSL Termination**: Can handle HTTPS encryption/decryption
4. **Load Balancing**: Can distribute traffic across multiple application instances

### Nginx Configuration Explained
In the deployment instructions, we set up Nginx as a reverse proxy with this configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Or EC2 public IP

    location / {
        proxy_pass http://localhost:8010;  # Forward to your app
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;  # Support WebSockets
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
}
```

- **listen 80**: Accept HTTP connections on port 80
- **proxy_pass**: Forward requests to your app running on localhost:8010
- **WebSocket Support**: Special headers to maintain WebSocket connections
- **Host header**: Preserve the original request's host information

## Systemd Service Management

The deployment uses systemd to manage your application as a system service:

```
[Unit]
Description=Search Agent with Google ADK
After=network.target

[Service]
User=ec2-user
WorkingDirectory=/home/ec2-user/Search-Agent/app
Environment="PATH=/home/ec2-user/Search-Agent/.venv/bin"
ExecStart=/home/ec2-user/Search-Agent/.venv/bin/uvicorn main:app --host 0.0.0.0 --port 8010

[Install]
WantedBy=multi-user.target
```

### Key Components:
- **User**: The service runs as `ec2-user` (not root for security)
- **WorkingDirectory**: Specifies where the application code is located
- **Environment**: Sets the PATH to include your virtual environment
- **ExecStart**: The command to run your application
- **WantedBy**: Makes the service start automatically at boot

### Useful systemd Commands
```bash
# Start the service
sudo systemctl start search-agent

# Stop the service
sudo systemctl stop search-agent

# Restart the service
sudo systemctl restart search-agent

# View service status
sudo systemctl status search-agent

# Enable service to start on boot
sudo systemctl enable search-agent

# View service logs
sudo journalctl -u search-agent -f
```

## Common Issues and Troubleshooting

### Connection Issues
If you can't connect to your EC2 instance:
1. **Check security group rules**: Ensure ports 22, 80, 443, and your app port are open
2. **Check SSH key permissions**: Must be restrictive (`chmod 400 your-key.pem`)
3. **Verify username**: Amazon Linux 2023 uses `ec2-user`, not `ubuntu`

### Application Not Accessible
If your app doesn't load when accessing your EC2 public IP:
1. **Check if the service is running**: `sudo systemctl status search-agent`
2. **Check Nginx configuration**: `sudo nginx -t`
3. **Check Nginx service**: `sudo systemctl status nginx`
4. **Check firewall**: `sudo iptables -L`
5. **Check application logs**: `sudo journalctl -u search-agent -f`

### WebSocket Connection Errors
If the app loads but WebSocket connections fail:
1. **Verify WebSocket headers** in Nginx configuration
2. **Check browser console** for connection errors
3. **Ensure app is binding** to 0.0.0.0 (not just localhost)

### Python/Dependency Issues
1. **Check Python version**: `python3 --version` (should be 3.9+)
2. **Verify virtual environment**: `which python` (should point to your .venv)
3. **Check pip installations**: `pip list`

## Security Best Practices

1. **Keep instance updated**: Run `sudo yum update` regularly
2. **Use secure passwords/keys** and don't share them
3. **Consider using HTTPS** with Let's Encrypt/Certbot
4. **Limit SSH access** to specific IP addresses when possible
5. **Run the app as a non-root user** (as shown in the service config)
6. **Back up your application data** regularly

## Cost Management

For AWS free tier users:
1. **Monitor usage**: Check AWS Billing Dashboard regularly
2. **Set up billing alarms** to be notified if approaching limits
3. **Stop or terminate** instances when not in use
4. **Use t2.micro** instance type to stay within free tier limits
5. **Be mindful of storage** and data transfer costs

## Helpful AWS CLI Commands

```bash
# Get information about your instance
aws ec2 describe-instances --instance-ids your-instance-id

# Stop an instance (can be restarted)
aws ec2 stop-instances --instance-ids your-instance-id

# Start a stopped instance
aws ec2 start-instances --instance-ids your-instance-id

# Terminate an instance (permanent)
aws ec2 terminate-instances --instance-ids your-instance-id
```

## Next Steps for Production Deployments

1. **Add monitoring**: Consider AWS CloudWatch or a similar service
2. **Implement backup strategy**: Regular database/file backups
3. **Set up CI/CD pipeline**: Automate deployments
4. **Configure auto-scaling**: For handling variable loads
5. **Use a custom domain name** with proper DNS configuration
6. **Implement HTTPS** with SSL/TLS certificates