from fastapi import FastAPI
from backend.repositories.conversation_repo.database import initialize_database
import uvicorn
import logging

from fastapi.middleware.cors import CORSMiddleware
from backend.api.router import api_router

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Agent Query API", description="API to handle user queries for an agent", version="1.0.0")


@app.on_event("startup")
def on_startup():
    logger.info("Application is starting up...")
    initialize_database()


origins = ["http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # We can use this to block certain commands [PUT,DELETE,ETC]
    allow_headers=["*"],  # [We can also block certain headers that we don't want]
)

app.include_router(api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
