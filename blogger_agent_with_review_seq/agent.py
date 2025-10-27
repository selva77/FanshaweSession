import os
from google.adk.agents import LlmAgent, SequentialAgent
from dotenv import load_dotenv
from google.adk.tools import google_search

load_dotenv()

blogger_agent = LlmAgent(
    name="blogger_agent_review",
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

root_agent = LlmAgent(
    name="blog_agent_with_review_seq",
    sub_agents=[blogger_agent, reviewer_agent],
    description="A pipeline that writes a blog post and then reviews it for quality."
)