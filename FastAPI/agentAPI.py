import time
import logging
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Initialize FastAPI application with metadata
app = FastAPI(title="Agent Query API", description="API to handle user queries for an agent", version="1.0.0")

# Initialize Logging
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Define the request model for user queries
class UserQueryRequest(BaseModel):
    query: str  # The query string provided by the user

# Endpoint to handle user queries
@app.post("/agent_query/")
async def agent_query(user_request: UserQueryRequest):
    startTime = time.time()
    logger.info(f"Received user request: {user_request.query}")

    query = user_request.query

    # Placeholder for agent processing logic
    # For now, just echoing back the query
    response = f"Received query: {query}"
    logger.info(f"Agent response: echo - {response}")

    endTime = time.time()
    logger.info(f"Total time taken: {endTime - startTime} seconds")

    # Return the response as a JSON object
    return {"response: ": response}