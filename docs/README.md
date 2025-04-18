# Search Agent

A real-time streaming agent built with the Google Agent Development Kit (ADK) that integrates Google Search capabilities and delivers responses via WebSockets.

## Features

- **Live Streaming Responses**: Get real-time streaming of AI responses as they're generated
- **Google Search Integration**: Grounded responses using Google Search for accurate information
- **WebSocket Communication**: Bidirectional communication between client and agent
- **Clean Web Interface**: Simple chat UI for interacting with the agent

## Prerequisites

- Python 3.9+
- [Google Agent Development Kit (ADK)](https://google.github.io/adk-docs/)
- A Google AI API key

## Setup

1. Clone this repository:
   ```bash
   git clone https://github.com/vikrampawar/Search-Agent.git
   cd Search-Agent
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install the Google ADK and required dependencies:
   ```bash
   pip install google-adk fastapi python-dotenv
   pip install "uvicorn[standard]"
   ```

4. Configure your API key:
   - Create a `.env` file in the `app` directory
   - Add your Google AI API key: `GOOGLE_API_KEY=your-api-key-here`

## Project Structure

```
Search-Agent/
├── app/
│   ├── main.py                # FastAPI application with WebSocket endpoints
│   ├── google_search_agent/
│   │   └── agent.py           # Agent implementation with Google Search tool
│   └── static/
│       └── index.html         # Web client interface
```

## Usage

From the `app` directory, run:
```bash
uvicorn main:app --reload --port 8010
```

Then open http://localhost:8000 in your browser to access the chat interface.

## How It Works

1. **FastAPI Server**: Serves the web interface and handles WebSocket connections
2. **WebSocket Communication**:
   - Client connects via WebSocket with a unique session ID
   - Server starts an agent session for each client
   - Bidirectional communication is established
3. **Streaming Responses**:
   - Agent responses are streamed in real-time to the client
   - The web interface updates as tokens are received

## Agent Capabilities

The application uses the Gemini 2.0 Flash model enhanced with Google Search capabilities, making it an effective research assistant that:
- Can search the web for information
- Provides real-time streaming responses
- Sticks to factual information

## Example Queries

Try asking the agent:
- "What are the latest developments in quantum computing?"
- "Tell me about the history of artificial intelligence."
- "What are the current trends in renewable energy?"
- "Explain the concept of WebSockets and their applications."

## Deployment to AWS EC2

### Prerequisites
- An AWS account
- Basic knowledge of AWS EC2 and security groups
- SSH client installed on your local machine

### Steps

1. **Launch an EC2 Instance**:
   - Log in to the AWS Management Console
   - Navigate to EC2 Dashboard and click "Launch Instance"
   - Select Amazon Linux 2023 (or Amazon Linux 2)
   - Choose an instance type (t2.micro for free tier or t2.small/t2.medium for better performance)
   - Configure security groups to allow:
     - SSH (port 22)
     - HTTP (port 80)
     - HTTPS (port 443)
     - Custom TCP for your app port (e.g., 8010)
   - Create or select a key pair for SSH access
   - Launch the instance

2. **Connect to Your Instance**:
   ```bash
   ssh -i ~/keys/vikramitwork-ec2-001-rsa.pem ec2-user@35.176.72.243
   ```

3. **Install Required Software**:
   ```bash
   # Update package lists
   sudo yum update -y
   sudo yum upgrade -y

   # Install Python and pip
   sudo yum install -y python3 python3-pip python3-devel

   # Install Nginx
   # OR for Amazon Linux 2023
   sudo yum install -y nginx
   
   # Start Nginx
   sudo systemctl start nginx
   sudo systemctl enable nginx
   ```

4. **Clone and Set Up the Application**:
   ```bash
   # Clone the repository
   git clone https://github.com/vikrampawar/Search-Agent.git
   cd Search-Agent

   # Create and activate virtual environment
   python3 -m venv .venv
   source .venv/bin/activate

   # Install dependencies
   pip install google-adk fastapi python-dotenv
   pip install "uvicorn[standard]"
   ```

5. **Configure Environment Variables**:
   ```bash
   cd app
   nano .env
   # Add your API key: GOOGLE_API_KEY=your-api-key-here
   ```

6. **Set Up Nginx as a Reverse Proxy**:
   ```bash
   # Create nginx configuration directory if it doesn't exist
   sudo mkdir -p /etc/nginx/conf.d
   
   # Create configuration file
   sudo vi /etc/nginx/conf.d/search-agent.conf
   ```

   Add the following configuration:
   ```nginx
   server {
       listen 80;
       server_name your-domain.com; # Or your EC2 public IP

       location / {
           proxy_pass http://localhost:8010;
           proxy_http_version 1.1;
           proxy_set_header Upgrade $http_upgrade;
           proxy_set_header Connection "upgrade";
           proxy_set_header Host $host;
           proxy_cache_bypass $http_upgrade;
       }
   }
   ```

   Test and restart Nginx:
   ```bash
   sudo nginx -t
   sudo systemctl restart nginx
   ```

7. **Run the Application as a Service**:
   ```bash
   sudo nano /etc/systemd/system/search-agent.service
   ```

   Add the following:
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

   Start and enable the service:
   ```bash
   sudo systemctl start search-agent
   sudo systemctl enable search-agent
   ```

8. **Access Your Application**:
   - Open a browser and navigate to your EC2 public IP or domain name
   - Your Search Agent should now be accessible

### SSL Configuration (Optional)

To secure your application with HTTPS:

1. **Install Certbot**:
   ```bash
   sudo yum install -y certbot python3-certbot-nginx
   ```

2. **Obtain SSL Certificate**:
   ```bash
   sudo certbot --nginx -d your-domain.com
   ```

3. **Follow the prompts** to complete the SSL setup

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.