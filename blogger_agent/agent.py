import os
from google.adk.agents import LlmAgent
from dotenv import load_dotenv
from google.adk.tools import google_search

load_dotenv()


root_agent = LlmAgent(
    name="blogger_agent",
    instruction="Write a blog post about the given topic. "
    "Before generating the blog ask the user to clarify the tone,"
     "length of the blog in number of words, type of audience, etc. in order to create an engaging blog.",
    model=os.getenv("GOOGLE_GENAI_MODEL"),
    tools=[google_search],
)