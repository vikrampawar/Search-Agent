#!/usr/bin/env python3
"""
EC2 Quick Check

A lightweight script to run directly on your EC2 instance to diagnose connectivity issues.
This script has minimal dependencies and should work on any Amazon Linux instance.

Usage:
    python ec2_quick_check.py
"""

import os
import socket
import subprocess
import platform
import urllib.request
from urllib.error import URLError

# ANSI color codes for better readability
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
END = '\033[0m'

def print_header(message):
    """Print a formatted header"""
    print(f"\n{BLUE}{BOLD}{'=' * 60}{END}")
    print(f"{BLUE}{BOLD} {message}{END}")
    print(f"{BLUE}{BOLD}{'=' * 60}{END}\n")

def print_result(name, status, message=None):
    """Print a formatted test result"""
    if status == "OK":
        status_color = GREEN
    elif status == "WARNING":
        status_color = YELLOW
    else:
        status_color = RED
    
    print(f"{BOLD}{name}:{END} {status_color}{status}{END}")
    if message:
        print(f"  → {message}")

def run_command(command):
    """Run a shell command and return its output"""
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True)
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def check_port(host, port):
    """Check if a port is open"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def main():
    print(f"{BOLD}EC2 Quick Check - Diagnostic Tool{END}")
    print("Testing connectivity and configuration issues...\n")

    # 1. System information
    print_header("System Information")
    os_info = run_command("cat /etc/os-release | grep PRETTY_NAME")
    kernel = run_command("uname -r")
    print_result("System", "INFO", os_info.replace('PRETTY_NAME=', '').replace('"', ''))
    print_result("Kernel", "INFO", kernel)
    
    # 2. Public IP information
    print_header("Network Information")
    try:
        with urllib.request.urlopen("http://checkip.amazonaws.com", timeout=3) as response:
            public_ip = response.read().decode('utf-8').strip()
            print_result("Public IP", "INFO", public_ip)
    except (URLError, socket.timeout):
        print_result("Public IP", "WARNING", "Could not determine public IP")

    # Check if we're in an EC2 instance
    try:
        with urllib.request.urlopen("http://169.254.169.254/latest/meta-data/instance-id", timeout=1) as response:
            instance_id = response.read().decode('utf-8')
            print_result("EC2 Instance", "OK", f"ID: {instance_id}")
            
            # Get additional metadata
            try:
                with urllib.request.urlopen("http://169.254.169.254/latest/meta-data/instance-type", timeout=1) as response:
                    instance_type = response.read().decode('utf-8')
                    print_result("Instance Type", "INFO", instance_type)
            except:
                pass
            
            try:
                with urllib.request.urlopen("http://169.254.169.254/latest/meta-data/placement/availability-zone", timeout=1) as response:
                    az = response.read().decode('utf-8')
                    print_result("Availability Zone", "INFO", az)
            except:
                pass
    except:
        print_result("EC2 Instance", "WARNING", "Not an EC2 instance or metadata service not available")

    # 3. Connectivity tests
    print_header("Connectivity Tests")
    
    # Internet connectivity
    try:
        with urllib.request.urlopen("http://www.google.com", timeout=3) as response:
            print_result("Internet Connectivity", "OK", "Connection to google.com successful")
    except:
        print_result("Internet Connectivity", "ERROR", "Could not connect to the internet")
    
    # Check important ports
    print_result("Port 22 (SSH)", "OK" if check_port('localhost', 22) else "WARNING", 
                 "Open" if check_port('localhost', 22) else "Closed or filtered")
    
    print_result("Port 80 (HTTP)", "OK" if check_port('localhost', 80) else "WARNING", 
                 "Open" if check_port('localhost', 80) else "Closed or filtered")
    
    print_result("Port 443 (HTTPS)", "OK" if check_port('localhost', 443) else "INFO", 
                 "Open" if check_port('localhost', 443) else "Closed or filtered")
    
    print_result("Port 8010 (App)", "OK" if check_port('localhost', 8010) else "WARNING", 
                 "Open" if check_port('localhost', 8010) else "Closed or filtered")

    # 4. Services status
    print_header("Service Status")
    nginx_status = run_command("systemctl is-active nginx")
    print_result("Nginx", "OK" if nginx_status == "active" else "ERROR", 
                 "Running" if nginx_status == "active" else f"Status: {nginx_status}")
    
    app_status = run_command("systemctl is-active search-agent")
    print_result("Search Agent", "OK" if app_status == "active" else "ERROR", 
                 "Running" if app_status == "active" else f"Status: {app_status}")

    # 5. Nginx configuration
    print_header("Nginx Configuration")
    
    # Check if Nginx config has WebSocket settings
    nginx_conf = ""
    for conf_path in ["/etc/nginx/conf.d/search-agent.conf", 
                     "/etc/nginx/sites-enabled/search-agent",
                     "/etc/nginx/sites-available/search-agent.conf"]:
        if os.path.exists(conf_path):
            nginx_conf = run_command(f"cat {conf_path}")
            break
    
    if nginx_conf:
        if "proxy_http_version 1.1" in nginx_conf and "Upgrade" in nginx_conf:
            print_result("WebSocket Config", "OK", "WebSocket configuration appears correct")
        else:
            print_result("WebSocket Config", "WARNING", "WebSocket headers might be missing in Nginx config")
        
        # Check for server_name
        if "server_name" in nginx_conf:
            server_name = run_command(f"grep server_name {conf_path} | head -1")
            print_result("Server Name", "INFO", server_name.strip())
    else:
        print_result("Nginx Config", "WARNING", "Could not locate Search Agent configuration file")
    
    # 6. Listening ports
    print_header("Listening Ports")
    ports = run_command("netstat -tulpn 2>/dev/null | grep LISTEN || ss -tulpn | grep LISTEN")
    if ports:
        print(ports)
    else:
        print_result("Ports", "WARNING", "Could not get listening ports (try running as root)")

    # 7. Security groups (if AWS CLI is available)
    aws_cli = run_command("which aws") != ""
    if aws_cli:
        print_header("Security Group Information")
        print("Run the following command to check security groups:")
        print(f"{YELLOW}aws ec2 describe-security-groups --group-ids $(aws ec2 describe-instances --instance-ids $(curl -s http://169.254.169.254/latest/meta-data/instance-id) --query 'Reservations[0].Instances[0].SecurityGroups[0].GroupId' --output text) --query 'SecurityGroups[0].IpPermissions[*]'{END}")
    
    # Summary
    print_header("Troubleshooting Summary")
    print("If your application isn't accessible externally:")
    print("1. Make sure both Nginx and Search Agent services are running")
    print("2. Check that port 80 is open in your EC2 security group")
    print("3. Verify that Nginx is correctly proxying to your application")
    print("4. Ensure WebSocket support is properly configured in Nginx")
    print("5. Check your application logs: sudo journalctl -u search-agent -f")
    print("6. Check Nginx logs: sudo tail -f /var/log/nginx/error.log")

if __name__ == "__main__":
    main()