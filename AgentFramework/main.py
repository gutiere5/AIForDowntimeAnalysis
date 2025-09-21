import logging
import time
import os
from fastapi import FastAPI
from pydantic import BaseModel
from agents import Agent
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Load OpenAI Credentials
api_key = os.getenv("OPENAI_API_KEY")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Agent Query API", description="API to handle user queries for an agent", version="1.0.0")

# Define Main LLM Agent/Model
main_agent = Agent(api_key=api_key)

# Define the request model for user queries
class UserQueryRequest(BaseModel):
    query: str  # The query string provided by the user

# Endpoint to handle user queries
@app.post("/agent_query/")
async def agent_query(user_request: UserQueryRequest):
    start_time = time.time()
    logger.info(f"Received user request: {user_request.query}")

    main_agent.receive_message(user_request.query)
    response = main_agent.generate_response()
    logger.info(f"Agent response: {response}")

    end_time = time.time()
    logger.info(f"Total time taken: {end_time - start_time} seconds")

    # Return the response as a JSON object
    return {"response": response}



