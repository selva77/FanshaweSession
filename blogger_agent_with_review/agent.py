import os
from google.adk.agents import LlmAgent, SequentialAgent, Agent
from google.adk.tools import AgentTool
from dotenv import load_dotenv
from google.adk.tools import google_search
from datetime import datetime
load_dotenv()

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


blogger_agent = Agent(
    name="blogger_agent",
    instruction="Write a blog post about the given topic. "
    "Before generating the blog ask the user to clarify the tone,"
     "length of the blog in number of words, type of audience, etc. in order to create an engaging blog.",
    model=os.getenv("GOOGLE_GENAI_MODEL"),
    tools=[google_search],
    output_key="blog_post",
)

reviewer_agent = LlmAgent(
    name="blog_reviewer_agent",
    instruction="Review the blog post  {blog_post} for clarity, engagement, grammar, and overall quality. "
    "Provide constructive feedback and suggest improvements if necessary."
        "Respond in a friendly and respectful manner.",
    model=os.getenv("GOOGLE_GENAI_MODEL"),
    output_key="review_feedback",
)

root_agent = Agent(
    name="blog_agent_with_review",
    instruction="You are a helpful assistant that writes a blog post and then reviews it for quality. "
    "Use the sub agents and tools to complete the task.",
    sub_agents=[reviewer_agent],
    tools=[AgentTool(blogger_agent),get_current_time],
    model=os.getenv("GOOGLE_GENAI_MODEL"),
)     



