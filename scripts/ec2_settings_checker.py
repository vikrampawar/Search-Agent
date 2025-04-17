#!/usr/bin/env python3
"""
EC2 Settings Checker

This script checks various settings and configurations on an Amazon EC2 instance
to help diagnose connectivity and deployment issues.

Usage:
    python ec2_settings_checker.py [--debug]
"""

import os
import sys
import socket
import subprocess
import argparse
import json
import re
import platform
from datetime import datetime
import requests
import urllib.request
from urllib.error import URLError


def run_command(command, return_output=True, show_command=True):
    """Run a shell command and return its output"""
    if show_command:
        print(f"\033[1;33m$ {command}\033[0m")  # Yellow color for commands
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        if result.returncode != 0 and result.stderr:
            print(f"\033[1;31mError: {result.stderr.strip()}\033[0m")  # Red for errors
            
        if return_output:
            return result.stdout.strip()
        else:
            if result.stdout:
                print(result.stdout.strip())
            return result.returncode == 0
    except Exception as e:
        print(f"\033[1;31mError executing command: {e}\033[0m")
        return None if return_output else False


def print_section(title):
    """Print a section title with formatting"""
    print(f"\n\033[1;36m{'=' * 50}\033[0m")
    print(f"\033[1;36m{title}\033[0m")
    print(f"\033[1;36m{'=' * 50}\033[0m\n")


def print_info(key, value, indent=0):
    """Print key-value information with formatting"""
    indent_str = " " * indent
    key_color = "\033[1;32m"  # Green
    reset = "\033[0m"
    print(f"{indent_str}{key_color}{key}:{reset} {value}")


def check_http_port(port=80):
    """Check if HTTP port is open and responding"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        
        if result == 0:
            try:
                response = requests.get(f"http://localhost:{port}", timeout=3)
                return True, response.status_code
            except requests.RequestException:
                return True, "Port open but no HTTP response"
        else:
            return False, "Port closed"
    except Exception as e:
        return False, str(e)


def check_aws_credentials():
    """Check if AWS credentials are configured"""
    # Check for AWS credentials or configuration
    aws_creds_exist = os.path.exists(os.path.expanduser('~/.aws/credentials'))
    aws_config_exists = os.path.exists(os.path.expanduser('~/.aws/config'))
    
    # Check AWS CLI version and if it's installed
    aws_cli_version = run_command("aws --version", show_command=False)
    aws_cli_installed = aws_cli_version and "aws-cli" in aws_cli_version
    
    return {
        "credentials_exist": aws_creds_exist,
        "config_exists": aws_config_exists,
        "cli_installed": aws_cli_installed,
        "cli_version": aws_cli_version if aws_cli_installed else "Not installed"
    }


def check_instance_metadata():
    """Get instance metadata from AWS metadata service"""
    metadata = {}
    try:
        # Check if this is actually an EC2 instance first
        try:
            # Timeout quickly if not an EC2 instance
            response = urllib.request.urlopen('http://169.254.169.254/latest/meta-data/', timeout=2)
            is_ec2 = True
        except (URLError, socket.timeout):
            is_ec2 = False
            return {"is_ec2_instance": False}
        
        metadata["is_ec2_instance"] = True
        
        # Get instance ID
        try:
            response = urllib.request.urlopen('http://169.254.169.254/latest/meta-data/instance-id')
            metadata["instance_id"] = response.read().decode('utf-8')
        except URLError:
            metadata["instance_id"] = "Not available"
            
        # Get instance type
        try:
            response = urllib.request.urlopen('http://169.254.169.254/latest/meta-data/instance-type')
            metadata["instance_type"] = response.read().decode('utf-8')
        except URLError:
            metadata["instance_type"] = "Not available"
            
        # Get public IPv4
        try:
            response = urllib.request.urlopen('http://169.254.169.254/latest/meta-data/public-ipv4')
            metadata["public_ip"] = response.read().decode('utf-8')
        except URLError:
            # Try alternative method to get public IP
            try:
                response = urllib.request.urlopen('http://checkip.amazonaws.com')
                metadata["public_ip"] = response.read().decode('utf-8').strip()
            except URLError:
                metadata["public_ip"] = "Not available"

        # Get availability zone
        try:
            response = urllib.request.urlopen('http://169.254.169.254/latest/meta-data/placement/availability-zone')
            metadata["availability_zone"] = response.read().decode('utf-8')
        except URLError:
            metadata["availability_zone"] = "Not available"

        # Get AMI ID
        try:
            response = urllib.request.urlopen('http://169.254.169.254/latest/meta-data/ami-id')
            metadata["ami_id"] = response.read().decode('utf-8')
        except URLError:
            metadata["ami_id"] = "Not available"
            
        return metadata
    except Exception as e:
        print(f"Error fetching instance metadata: {e}")
        return {"is_ec2_instance": False, "error": str(e)}


def check_security_groups(aws_cli_works=False):
    """Get security group information"""
    if not aws_cli_works:
        return {"available": False, "message": "AWS CLI not configured or installed"}
    
    instance_id = run_command("curl -s http://169.254.169.254/latest/meta-data/instance-id")
    if not instance_id or "404 Not Found" in instance_id:
        return {"available": False, "message": "Not an EC2 instance or metadata not available"}
        
    # Get security groups
    sg_info = run_command(f"aws ec2 describe-instance-attribute --instance-id {instance_id} --attribute groupSet --region $(curl -s http://169.254.169.254/latest/meta-data/placement/region) --output json")
    try:
        sg_data = json.loads(sg_info)
        return {"available": True, "data": sg_data}
    except Exception:
        return {"available": False, "message": "Could not parse security group information"}


def check_system_info():
    """Collect system information"""
    info = {
        "os": platform.system(),
        "release": platform.release(),
        "hostname": platform.node(),
        "distribution": "Unknown"
    }
    
    # Get Linux distribution info
    if platform.system() == "Linux":
        # Try to get more specific Linux distribution info
        if os.path.exists('/etc/os-release'):
            os_release = run_command("cat /etc/os-release")
            pretty_name_match = re.search(r'PRETTY_NAME="([^"]+)"', os_release)
            if pretty_name_match:
                info["distribution"] = pretty_name_match.group(1)
                
            # Check if it's Amazon Linux specifically
            if "amazon" in os_release.lower():
                if os.path.exists('/etc/system-release'):
                    info["amazon_linux_version"] = run_command("cat /etc/system-release")
    
    return info


def check_firewall():
    """Check firewall status and rules"""
    result = {}
    
    # Check iptables (basic Linux firewall)
    iptables_present = run_command("which iptables") != ""
    result["iptables_present"] = iptables_present
    
    if iptables_present:
        iptables_rules = run_command("sudo iptables -L -n")
        result["iptables_rules"] = iptables_rules if iptables_rules else "No rules or permission denied"
    
    # Check firewalld (CentOS/RHEL/Amazon Linux 2)
    firewalld_present = run_command("which firewall-cmd") != ""
    result["firewalld_present"] = firewalld_present
    
    if firewalld_present:
        firewalld_running = "running" in run_command("sudo systemctl status firewalld")
        result["firewalld_running"] = firewalld_running
        
        if firewalld_running:
            zones = run_command("sudo firewall-cmd --list-all-zones")
            result["firewalld_zones"] = zones
    
    # Check ufw (Ubuntu)
    ufw_present = run_command("which ufw") != ""
    result["ufw_present"] = ufw_present
    
    if ufw_present:
        ufw_status = run_command("sudo ufw status")
        result["ufw_status"] = ufw_status
    
    return result


def check_service_status():
    """Check the status of relevant services"""
    services = {
        "nginx": run_command("sudo systemctl is-active nginx"),
        "search-agent": run_command("sudo systemctl is-active search-agent")
    }
    
    # Get more details about search-agent service
    if services["search-agent"] == "active":
        services["search-agent_details"] = run_command("sudo systemctl status search-agent | head -20")
    
    return services


def check_listening_ports():
    """Check which ports are listening"""
    # Use ss or netstat to check listening ports
    if run_command("which ss") != "":
        ports = run_command("ss -tulpn | grep LISTEN")
    else:
        ports = run_command("netstat -tulpn | grep LISTEN")
    
    return ports


def check_nginx_config():
    """Check Nginx configuration"""
    result = {}
    
    # Check if Nginx is installed
    nginx_installed = run_command("which nginx") != ""
    result["installed"] = nginx_installed
    
    if nginx_installed:
        # Check Nginx syntax
        syntax_check = run_command("sudo nginx -t 2>&1")
        result["syntax_check"] = syntax_check
        
        # Get Nginx version
        version = run_command("nginx -v 2>&1")
        result["version"] = version
        
        # Check if search-agent configuration exists
        search_agent_conf_exists = False
        
        # Check in common Nginx configuration directories
        for conf_dir in ["/etc/nginx/conf.d/", "/etc/nginx/sites-available/", "/etc/nginx/sites-enabled/"]:
            if os.path.exists(conf_dir):
                files = run_command(f"ls -la {conf_dir}")
                result[f"files_in_{conf_dir}"] = files
                
                if "search-agent" in files:
                    search_agent_conf_exists = True
                    result["search_agent_conf_location"] = conf_dir
                    result["search_agent_conf_content"] = run_command(f"cat {conf_dir}/search-agent.conf")
        
        result["search_agent_conf_exists"] = search_agent_conf_exists
    
    return result


def check_connectivity():
    """Check connectivity to the outside world"""
    result = {}
    
    # Check internet connectivity
    try:
        response = urllib.request.urlopen('http://www.google.com', timeout=5)
        result["internet_connectivity"] = True
    except (URLError, socket.timeout):
        result["internet_connectivity"] = False
    
    # Try to get public IP
    try:
        response = urllib.request.urlopen('http://checkip.amazonaws.com', timeout=5)
        result["public_ip"] = response.read().decode('utf-8').strip()
    except (URLError, socket.timeout):
        result["public_ip"] = "Not available"
    
    # Test ports 80 and 8010 internally
    http_status, http_details = check_http_port(80)
    result["port_80_status"] = "Open" if http_status else "Closed"
    result["port_80_details"] = http_details
    
    app_status, app_details = check_http_port(8010)
    result["port_8010_status"] = "Open" if app_status else "Closed"
    result["port_8010_details"] = app_details
    
    return result


def main():
    parser = argparse.ArgumentParser(description='Check AWS EC2 settings and connectivity')
    parser.add_argument('--debug', action='store_true', help='Show more detailed output')
    args = parser.parse_args()
    
    print(f"\033[1m\nEC2 Settings Checker - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\033[0m")
    
    # Check system information
    print_section("System Information")
    system_info = check_system_info()
    for key, value in system_info.items():
        print_info(key, value)
    
    # Check if this is an EC2 instance
    metadata = check_instance_metadata()
    is_ec2 = metadata.get("is_ec2_instance", False)
    
    print_section("EC2 Instance Information")
    if is_ec2:
        print_info("Is EC2 Instance", "Yes")
        for key, value in metadata.items():
            if key != "is_ec2_instance":
                print_info(key, value)
    else:
        print_info("Is EC2 Instance", "No")
        print("This doesn't appear to be an EC2 instance or the metadata service is not accessible.")
    
    # Check AWS CLI and credentials
    print_section("AWS Credentials")
    aws_info = check_aws_credentials()
    for key, value in aws_info.items():
        print_info(key, value)
    
    # Check security groups if this is an EC2 instance and AWS CLI works
    if is_ec2 and aws_info["cli_installed"]:
        print_section("Security Groups")
        sg_info = check_security_groups(True)
        if sg_info["available"]:
            print_info("Security Groups", "Available")
            if args.debug:
                print(json.dumps(sg_info["data"], indent=2))
            else:
                print("Use --debug to see security group details")
        else:
            print_info("Security Groups", f"Not available: {sg_info['message']}")
    
    # Check connectivity
    print_section("Network Connectivity")
    connectivity = check_connectivity()
    for key, value in connectivity.items():
        print_info(key, value)
    
    # Check listening ports
    print_section("Listening Ports")
    ports = check_listening_ports()
    print(ports if ports else "No listening ports found or permission denied")
    
    # Check Nginx configuration
    print_section("Nginx Configuration")
    nginx_info = check_nginx_config()
    for key, value in nginx_info.items():
        if key not in ["search_agent_conf_content", "files_in_/etc/nginx/conf.d/", 
                       "files_in_/etc/nginx/sites-available/", "files_in_/etc/nginx/sites-enabled/"]:
            print_info(key, value)
    
    # Show search-agent configuration if it exists
    if nginx_info.get("search_agent_conf_exists", False):
        print_section("Search Agent Nginx Configuration")
        print(nginx_info.get("search_agent_conf_content", ""))
    
    # Check service status
    print_section("Service Status")
    services = check_service_status()
    for key, value in services.items():
        if not key.endswith("_details"):
            print_info(key, value)
    
    if "search-agent_details" in services:
        print_section("Search Agent Service Details")
        print(services["search-agent_details"])
    
    # Check firewall if in debug mode
    if args.debug:
        print_section("Firewall Information")
        firewall_info = check_firewall()
        for key, value in firewall_info.items():
            if not isinstance(value, str) or len(value) < 100:
                print_info(key, value)
            else:
                print_info(key, "Available (too long to display)")
                if key == "iptables_rules":
                    print("\nIPTables Rules:")
                    print(value)


if __name__ == "__main__":
    main()