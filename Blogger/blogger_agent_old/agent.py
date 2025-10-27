import os
from google.adk.agents import LlmAgent
from dotenv import load_dotenv

load_dotenv()


root_agent = LlmAgent(
    name="blogger_agent",
    instruction="Write a blog post about the given topic {topic} in a friendly and engaging tone.",
    model=os.getenv("GOOGLE_GENAI_MODEL"),
)