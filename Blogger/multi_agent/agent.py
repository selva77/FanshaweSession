import os
from google.adk.agents import LlmAgent
from dotenv import load_dotenv
from google.adk.tools import google_search
from .subagents.knockknock_agent.agent import knockknock_agent

load_dotenv()

def get_current_time() -> dict:
    from datetime import datetime
    now = datetime.now()
    return {
        "year": now.year,
        "month": now.month,
        "day": now.day,
        "hour": now.hour,
        "minute": now.minute,
        "second": now.second,
    }

root_agent = LlmAgent(
    name="multi_agent",
    instruction="You are a master agent that can delegate tasks to specialized sub-agents.",
    #tools=[google_search],
   tools=[get_current_time],
   sub_agents=[knockknock_agent],
   model=os.getenv("GOOGLE_GENAI_MODEL"),
)