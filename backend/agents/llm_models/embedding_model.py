from sentence_transformers import SentenceTransformer
import logging

logger = logging.getLogger(__name__)

# Initialize the model once and share it across the application.
# This is a simple way to create a singleton instance.
try:
    logger.info("Loading shared SentenceTransformer model...")
    EMBEDDING_MODEL = SentenceTransformer('all-MiniLM-L6-v2')
    logger.info("Shared SentenceTransformer model loaded successfully.")
except Exception as e:
    logger.error(f"Failed to load the SentenceTransformer model: {e}")
    # If the model fails to load, we can set it to None and handle it gracefully elsewhere,
    # or re-raise the exception to halt startup. For now, we re-raise.
    raise e
