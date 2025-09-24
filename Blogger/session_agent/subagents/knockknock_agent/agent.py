import os
from google.adk.agents import LlmAgent
#from dotenv import load_dotenv

#load_dotenv()

knockknock_agent = LlmAgent(
    name="knockknock_agent",
    description="An agent that tells knock knock jokes",
    instruction="Write a knock knock joke about in a friendly and respectful way",
    model=os.getenv("GOOGLE_GENAI_MODEL"),
)