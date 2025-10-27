import uvicorn
import logging
from fastapi.responses import StreamingResponse, JSONResponse
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.agent_orchestrator import AgentOrchestrator
import json

# Load environment variables from .env file
load_dotenv()

# Load API Key Credentials
OPENAI_TOKEN = os.getenv("OPENAI_API_KEY")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# Initialize FastAPI app
app = FastAPI(title="Agent Query API", description="API to handle user queries for an agent", version="1.0.0")

# Define Main LLM Agent/Model
main_agent = AgentOrchestrator(api_key=HUGGINGFACE_TOKEN)

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

# Define the request model for log entries
class LogEntry(BaseModel):
    id: int
    timestamp: str
    machine_id: str
    reason_code: str
    duration_minutes: int

# Endpoint to handle user queries
@app.post("/agent_query")
async def agent_query(user_request: UserQueryRequest):
    logger.info(f"Received user request: {user_request.query}")

    return StreamingResponse(
        main_agent.process_query(user_request.query),
        media_type="text/event-stream"
    )

@app.post("/index_log")
async def index_log(log_entry: LogEntry):
    logger.info(f"Received log entry for indexing: {log_entry.dict()}")
    log_entry_json = json.dumps(log_entry.dict())
    # The agent orchestrator expects a query string, so we'll format it as a tool call
    tool_call_query = f"Call: index_log_entry(log_entry_json='''{log_entry_json}''')"
    
    # Process the query through the agent orchestrator
    # We expect a direct tool execution here, not a conversational response
    response_generator = main_agent.process_query(tool_call_query)
    
    # Extract the final response from the generator
    final_response = ""
    async for chunk in response_generator:
        # Assuming the tool output is returned as a single chunk or the last chunk
        try:
            data = json.loads(chunk.replace("data: ", ""))
            if data.get("type") == "chunk":
                final_response += data.get("content", "")
            elif data.get("type") == "done":
                break
        except json.JSONDecodeError:
            # Handle cases where chunk is not valid JSON, e.g., direct tool output
            final_response += chunk.replace("data: ", "")

    # The tool itself returns a JSON string, so we need to parse it
    try:
        tool_output = json.loads(final_response)
        return JSONResponse(content=tool_output)
    except json.JSONDecodeError:
        return JSONResponse(content={"status": "error", "message": f"Unexpected response from tool: {final_response}"}, status_code=500)


@app.post("/search_logs")
async def search_logs(user_request: UserQueryRequest):
    logger.info(f"Received search query for logs: {user_request.query}")
    tool_call_query = f"Call: search_indexed_logs(query_text='''{user_request.query}''')"

    response_generator = main_agent.process_query(tool_call_query)

    final_response = ""
    async for chunk in response_generator:
        try:
            data = json.loads(chunk.replace("data: ", ""))
            if data.get("type") == "chunk":
                final_response += data.get("content", "")
            elif data.get("type") == "done":
                break
        except json.JSONDecodeError:
            final_response += chunk.replace("data: ", "")
    
    try:
        tool_output = json.loads(final_response)
        return JSONResponse(content=tool_output)
    except json.JSONDecodeError:
        return JSONResponse(content={"status": "error", "message": f"Unexpected response from tool: {final_response}"}, status_code=500)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)