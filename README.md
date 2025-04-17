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
uvicorn main:app --reload
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

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.