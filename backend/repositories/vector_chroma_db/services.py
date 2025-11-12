import logging
from backend.api.schemas import LogEntry
from backend.agents.tools.log_processor import log_to_text, generate_embedding
from backend.repositories.vector_chroma_db.chroma_client import ChromaClient

logger = logging.getLogger(__name__)

async def index_log(log_entry: LogEntry) -> dict:
    """
    Index a log entry by generating its embedding and storing it in the vector database.
    """
    try:
        logger.info(f"Indexing log entry: {log_entry.dict()}")

        chroma_client_instance = ChromaClient(collection_name="log_embeddings")

        log_entry_dict = log_entry.dict()
        text_representation = log_to_text(log_entry_dict)
        embedding = generate_embedding(text_representation)

        if embedding:
            chroma_client_instance.add_log_embedding(text_representation, embedding, metadata=log_entry_dict)
            return {"status": "success", "message": "Log entry indexed successfully."}
        else:
            logger.warning("Failed to generate embedding for log entry.")
            return {"status": "error", "message": "Failed to generate embedding for log entry.", "status_code": 500}
    except Exception as e:
        logger.error(f"Error indexing log entry: {e}")
        return {"status": "error", "message": str(e), "status_code": 500}