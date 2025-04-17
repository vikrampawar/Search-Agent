from google.adk.agents import Agent
from google.adk.tools import google_search  # Import the tool

root_agent = Agent(
    # A unique name for the agent.
    name="basic_search_agent",
    
    # The Large Language Model (LLM) that agent will use.
    model="gemini-2.0-flash-exp",
    
    # A short description of the agent's purpose.
    description="A basic search agent with streaming capabilities",
    
    # Instructions to set the agent's behavior.
    instruction="You are an expert researcher. You always stick to the facts.",
    
    # Add google_search tool to perform grounding with Google search.
    tools=[google_search]
)
