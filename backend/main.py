import uvicorn
import logging
from fastapi.responses import StreamingResponse
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.agents.agent_orchestrator import AgentOrchestrator

# Load environment variables from .env file
load_dotenv()

# Load API Key Credentials
OPENAI_TOKEN = os.getenv("OPENAI_API_KEY")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Adding tools, move somewhere else later

# Initialize FastAPI app
app = FastAPI(title="Agent Query API", description="API to handle user queries for an agent", version="1.0.0")

# Define Main LLM Agent/Model
main_agent = AgentOrchestrator(api_key=HUGGINGFACE_TOKEN)
# main_agent = AgentHuggingFace(api_key=HUGGINGFACE_TOKEN)
# main_agent.add_tool(query_database_tool)
# main_agent.add_tool(analyze_trend_tool)

origins = [
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # We can use this to block certain commands [PUT,DELETE,ETC]
    allow_headers=["*"], #[We can also block certain headers that we don't want]
)

@app.head('/health')
@app.get('/health')
def health_check():
    return 'ok'

# Define the request model for user queries
class UserQueryRequest(BaseModel):
    query: str  # The query string provided by the user

# Endpoint to handle user queries
@app.post("/agent_query")
async def agent_query(user_request: UserQueryRequest):
    logger.info(f"Received user request: {user_request.query}")
    # main_agent.receive_message(user_request.query)

    return StreamingResponse(
        #main_agent.generate_test_response(),
        # main_agent.generate_response(),
        main_agent.process_query(user_request.query),
        media_type="text/event-stream"
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)