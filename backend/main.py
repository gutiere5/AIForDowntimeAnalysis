# Imports from 'main' branch
from fastapi import FastAPI, HTTPException
from backend.database import initialize_database
from agents.request_context import RequestContext
from typing import Optional

# Your original imports
import uvicorn
import logging
from fastapi.responses import StreamingResponse, JSONResponse
import os
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Imports from BOTH branches, correctly merged
from backend.agents.agent_orchestrator import AgentOrchestrator # Your 'backend.' path
import json # Your import
import uuid # 'main' branch's import

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

# 'main' branch's new startup event
@app.on_event("startup")
def on_startup():
    """Event handler for application startup."""
    logger.info("Application is starting up...")
    initialize_database()

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

# --- Your new endpoint ---
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

# 'main' branch's modified UserQueryRequest
class UserQueryRequest(BaseModel):
    query: str  # The query string provided by the user
    conversation_id: Optional[str] = None
    session_id: Optional[str] = None

# 'main' branch's new HistoryRequest
class HistoryRequest(BaseModel):
    conversation_id: str
    session_id: str

# Your LogEntry class
class LogEntry(BaseModel):
    id: int
    timestamp: str
    machine_id: str
    reason_code: str
    duration_minutes: int

# 'main' branch's modified /agent_query
@app.post("/agent_query")
async def agent_query(user_request: UserQueryRequest):
    logger.info(f"Received user request: {user_request.query}")
    
    if not user_request.session_id:
        raise HTTPException(status_code=400, detail="session_id is required")

    context = RequestContext(
        session_id=user_request.session_id,
        conversation_id=user_request.conversation_id or str(uuid.uuid4())
    )

    return StreamingResponse(
        main_agent.process_query(user_request.query, context),
        media_type="text/event-stream"
    )

# Your /index_log endpoint
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

# 'main' branch's new /get_history endpoint
@app.post("/get_history")
async def get_history(history_request: HistoryRequest):
    from backend.repositories import conversations_repository
    logger.info(f"Fetching history for conversation_id: {history_request.conversation_id}")
    messages = conversations_repository.get_messages_by_conversation_id(
        history_request.conversation_id,
        history_request.session_id
    )
    return {"messages": messages}

# 'main' branch's new /conversations/{session_id} endpoint
@app.get("/conversations/{session_id}")
async def get_conversations(session_id: str):
    from backend.repositories import conversations_repository
    logger.info(f"Fetching all conversations for session_id: {session_id}")
    conversations = conversations_repository.get_conversations_by_session_id(session_id)
    return {"conversations": conversations}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)