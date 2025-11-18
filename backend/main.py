
import uvicorn
import logging
from fastapi.responses import StreamingResponse, JSONResponse
import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from backend.agents.agent_orchestrator import AgentOrchestrator
import json

# Load environment variables from .env file
load_dotenv()  # Loads the main .env file (for secrets)
load_dotenv(dotenv_path=".env.build", override=True) # Loads and overrides with build info

# Load API Key Credentials
OPENAI_TOKEN = os.getenv("OPENAI_API_KEY")
HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")

# Load Build & Environment Info
APP_COMMIT_HASH = os.getenv("APP_COMMIT_HASH", "unknown")
APP_BUILD_DATE = os.getenv("APP_BUILD_DATE", "unknown")
APP_ENV = os.getenv("APP_ENV", "development") # Default to 'development' if not set

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
# --- ADD THE NEW ENDPOINT HERE ---
@app.get("/about")
def get_about_info():
    """
    Returns build and environment information for the running application.
    """
    return {
        "app_version": app.version,
        "environment": APP_ENV,
        "commit_hash": APP_COMMIT_HASH,
        "build_date": APP_BUILD_DATE,
    }
# --- END OF NEW ENDPOINT ---
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
    try:
        from backend.tools.log_processor import log_to_text, generate_embedding
        from backend.vector_chroma_db.chroma_client import ChromaClient

        chroma_client_instance = ChromaClient(collection_name="log_embeddings")
        
        log_entry_dict = log_entry.dict()
        text_representation = log_to_text(log_entry_dict)
        embedding = generate_embedding(text_representation)

        if embedding:
            chroma_client_instance.add_log_embedding(text_representation, embedding, metadata=log_entry_dict)
            return JSONResponse(content={"status": "success", "message": "Log entry indexed successfully."})
        else:
            return JSONResponse(content={"status": "error", "message": "Failed to generate embedding for log entry."}, status_code=500)
    except Exception as e:
        logger.error(f"Error indexing log entry: {e}")
        return JSONResponse(content={"status": "error", "message": str(e)}, status_code=500)



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