
import logging
from typing import AsyncGenerator, List, Dict, Any
from typing_extensions import override
from pydantic import BaseModel, Field
import json

from google.adk.agents import LlmAgent, BaseAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.events import Event
from dotenv import load_dotenv

load_dotenv()

# --- Constants ---
APP_NAME = "car_dealership_app"
USER_ID = "test_user_123"
SESSION_ID = "car_session_456"
GEMINI_MODEL = "gemini-2.5-flash"

# --- Configure Logging ---
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Tool Definitions ---

class CarInventoryToolInput(BaseModel):
    car_type: str = Field(description="The type of car the user is looking for (e.g., 'sedan', 'SUV', 'truck').")
    new_or_preowned: str = Field(description="Whether the user wants a 'new' or 'pre-owned' car.")
    budget: int = Field(description="The maximum budget the user has for the car.")

def check_inventory(car_type: str, new_or_preowned: str, budget: int) -> List[Dict[str, Any]]:
    """
    Simulates checking the car inventory based on user preferences.
    Returns a list of dictionaries, where each dictionary represents a car.
    """
    logger.info(f"Checking inventory for: Type={car_type}, Condition={new_or_preowned}, Budget=${budget}")
    
    # Simulated inventory
    inventory = [
        {"make": "Honda", "model": "Civic", "type": "sedan", "condition": "new", "price": 25000},
        {"make": "Toyota", "model": "RAV4", "type": "SUV", "condition": "pre-owned", "price": 28000},
        {"make": "Ford", "model": "F-150", "type": "truck", "condition": "new", "price": 45000},
        {"make": "BMW", "model": "X5", "type": "SUV", "condition": "pre-owned", "price": 35000},
        {"make": "Mercedes", "model": "C-Class", "type": "sedan", "condition": "new", "price": 40000},
        {"make": "Nissan", "model": "Titan", "type": "truck", "condition": "pre-owned", "price": 30000},
        {"make": "Honda", "model": "CRV", "type": "SUV", "condition": "new", "price": 32000},
        {"make": "Toyota", "model": "Camry", "type": "sedan", "condition": "pre-owned", "price": 22000},
    ]

    matching_cars = []
    for car in inventory:
        if (car["type"].lower() == car_type.lower() and
            car["condition"].lower() == new_or_preowned.lower() and
            car["price"] <= budget):
            matching_cars.append(car)
    
    if not matching_cars:
        logger.info("No cars found matching the criteria.")
        return [{"message": "No cars found matching your criteria. Please try different preferences."}]
    
    logger.info(f"Found {len(matching_cars)} matching cars.")
    return matching_cars

class AppointmentToolInput(BaseModel):
    car_make: str = Field(description="The make of the car for the test drive.")
    car_model: str = Field(description="The model of the car for the test drive.")
    date: str = Field(description="The desired date for the test drive (e.g., 'YYYY-MM-DD').")
    time: str = Field(description="The desired time for the test drive (e.g., 'HH:MM AM/PM').")

def book_test_drive(car_make: str, car_model: str, date: str, time: str) -> str:
    """
    Simulates booking a test drive for a specific car.
    Returns a confirmation message.
    """
    logger.info(f"Attempting to book test drive for {car_make} {car_model} on {date} at {time}.")
    # Simulate a successful booking
    confirmation_message = (
        f"Your test drive for the {car_make} {car_model} has been successfully booked "
        f"for {date} at {time}. A confirmation email will be sent shortly."
    )
    logger.info(confirmation_message)
    return confirmation_message

# --- Agent Definitions ---

# Lead Agent: Initial Contact & Qualification
lead_agent = LlmAgent(
    name="LeadAgent",
    model=GEMINI_MODEL,
    instruction="""You are the initial contact agent for a car dealership.
    Your goal is to gather essential information from the user:
    1. The type of car they are looking for (e.g., sedan, SUV, truck).
    2. Whether they want a new or pre-owned car.
    3. Their maximum budget.
    
    Once you have all three pieces of information, store them in the session state with keys 'car_type', 'new_or_preowned', and 'budget' respectively.
    Then, indicate that the lead is qualified and ready to be transferred to the Inventory Agent.
    """,
    output_key="lead_qualification_status",
)

# Inventory Agent
inventory_agent = LlmAgent(
    name="InventoryAgent",
    model=GEMINI_MODEL,
    instruction="""You are the Inventory Agent. Your task is to recommend vehicles based on the user's preferences.
    Access the session state to get 'car_type', 'new_or_preowned', and 'budget' set by the Lead Agent.
    Use the 'check_inventory' tool to find matching cars.
    Present the matching cars to the user in a clear, concise list.
    If no cars are found, inform the user and suggest they try different preferences.
    Store the recommended cars in the session state under the key 'recommended_cars'.
    """,
    tools=[check_inventory],
    output_key="inventory_recommendation",
)

# Appointment Agent
appointment_agent = LlmAgent(
    name="AppointmentAgent",
    model=GEMINI_MODEL,
    instruction="""You are the Appointment Agent. Your role is to book a test drive for a specific car.
    Access the session state to get the 'recommended_cars' from the Inventory Agent.
    Ask the user which car they would like to test drive, and for a preferred date and time.
    Once you have the car details, date, and time, use the 'book_test_drive' tool to book the appointment.
    Confirm the booking with the user.
    """,
    tools=[book_test_drive],
    output_key="appointment_confirmation",
)

root_agent = LlmAgent(
    name="CarDealershipCoordinator",
    instruction="""A coordinator agent that manages the car dealership support process from lead qualification to inventory recommendation and appointment booking.
    as the root agent, you should not respond directly to the user but instead delegate to the sub-agents as needed.""",
    model=GEMINI_MODEL,
     sub_agents=[
        lead_agent,
        inventory_agent,
        appointment_agent,
    ],
)
# --- Coordinator Agent ---
#root_agent = SequentialAgent(
 #   name="CarDealershipCoordinator",
  #  sub_agents=[
   #     lead_agent,
    #    inventory_agent,
     #   appointment_agent,
    #],
#)

# --- Application Execution ---
async def run_car_dealership_system(user_input: str):
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID, state={}
    )
    logger.info(f"Initial session state: {session.state}")

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    content = types.Content(role='user', parts=[types.Part(text=user_input)])
    events = runner.run_async(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    final_response = "No final response captured."
    async for event in events:
        if event.is_final_response() and event.content and event.content.parts:
            logger.info(f"Potential final response from [{event.author}]: {event.content.parts[0].text}")
            final_response = event.content.parts[0].text

    print("\n--- Agent Interaction Result ---")
    print("Agent Final Response: ", final_response)

    final_session = await session_service.get_session(
        app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID
    )
    print("Final Session State:")
    print(json.dumps(final_session.state, indent=2))
    print("-------------------------------\\n")

# Example usage (you would typically run this from another script or directly in an async context)
async def main():
    print("Starting Car Dealership Support System...")
    # Initial user query to the Lead Agent
    await run_car_dealership_system("I'm looking for a new sedan with a budget of $25000.")
    # Subsequent queries would continue the conversation, building on the session state
    # For a full interactive experience, you'd need a loop to take continuous user input.

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
