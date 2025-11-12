import logging
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from backend.api.schemas import LogEntry
from backend.repositories.vector_chroma_db import services

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/index_log")
async def index_log(log_entry: LogEntry):
    logger.info(f"Received the log entry for indexing: {log_entry.dict()}")
    result = services.index_log(log_entry)
    status_code = result.pop("status_code", 200)

    return JSONResponse(content=result, status_code=status_code)