import logging
from fastapi import APIRouter, HTTPException
import os

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/about")
def get_about_info():
    """
    Returns build and environment information for the running application.
    """
    # Load Build & Environment Info
    APP_COMMIT_HASH = os.getenv("APP_COMMIT_HASH", "unknown")
    APP_BUILD_DATE = os.getenv("APP_BUILD_DATE", "unknown")
    APP_ENV = os.getenv("APP_ENV", "development")  # Default to 'development' if not set

    return {
        "environment": APP_ENV,
        "commit_hash": APP_COMMIT_HASH,
        "build_date": APP_BUILD_DATE,
    }
