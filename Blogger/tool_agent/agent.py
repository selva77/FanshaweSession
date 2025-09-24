import os
from google.adk.agents import LlmAgent
from dotenv import load_dotenv
from google.adk.tools import google_search

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
    name="tool_agent",
    instruction="You are an assistant that can use tools to help answer user queries. Use the tools when necessary to provide accurate and up-to-date information.",
    model=os.getenv("GOOGLE_GENAI_MODEL"),
    tools=[google_search],
   #tools=[get_current_time],
   
)