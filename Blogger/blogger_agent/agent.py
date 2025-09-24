import os
from google.adk.agents import LlmAgent
from dotenv import load_dotenv

load_dotenv()

root_agent = LlmAgent(
    name="blogger_agent",
    instruction="Just say, I am a blogger agent, if prompted by user.",
    model=os.getenv("GOOGLE_GENAI_MODEL"),
)