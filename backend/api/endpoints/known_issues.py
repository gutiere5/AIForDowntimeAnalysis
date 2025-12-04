import logging
from fastapi import APIRouter, HTTPException, Response, status
from backend.repositories.sql_databases import known_issues_repo
from backend.repositories.vector_chroma_db.chroma_client import ChromaClient

logger = logging.getLogger(__name__)
router = APIRouter()
chroma_client = ChromaClient("known_issues")

@router.post("/known_issues/")
async def create_issue(title, description, solution, author):
    logger.info(f"creating known issue in relational database")
    issue_id = known_issues_repo.create_issue(title, description, solution, author)
    if not issue_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create known issue in the database")

    logger.info(f"creating known issue in vector database")
    documents_content = f"Title:{title}. Description:{description}. Solution:{solution}."
    metadata = {"title": title, "description": description, "solution": solution, "author": author}
    chroma_client.add_single_item(ids=issue_id, document=documents_content, metadata=metadata)

    created_issue = known_issues_repo.get_issue_by_id(issue_id)
    return created_issue

@router.get("/known_issues/{issue_id}")
async def get_issue(issue_id):
    logger.info(f"getting issue with id: {issue_id}")
    issue = known_issues_repo.get_issue_by_id(issue_id)
    if not issue:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Known Issue not found.")
    return {"issue": issue}

@router.get("/known_issues/")
async def get_all_known_issues():
    logger.info(f"get all known issues")
    issues = known_issues_repo.get_all_issues()
    return {"known_issues": issues}

@router.put("/known_issues/{issue_id}")
async def update_issue(issue_id, title, description, solution, author):
    logger.info(f"updating known issue with id: {issue_id}")
    update_issue_id = known_issues_repo.update_issue(issue_id, title, description, solution, author)
    if not update_issue_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update known issue in the database"
        )

    logger.info(f"updating known issue in vector database with id: {issue_id}")
    documents_content = f"Title:{title}. Description:{description}. Solution:{solution}."
    metadata = {"title": title, "description": description, "solution": solution, "author": author}
    chroma_client.upsert_single_item(id=issue_id, document=documents_content, metadata=metadata)

    updated_issue = known_issues_repo.get_issue_by_id(update_issue_id)
    return updated_issue

@router.delete("/known_issues/{issue_id}")
async def delete_issue(issue_id):
    logger.info(f"deleting known issue with id: {issue_id}")
    deleted_issue_id = known_issues_repo.delete_issue(issue_id)
    if not deleted_issue_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to delete known issue in the database"
        )
    logger.info(f"deleting known issue from vector database with id: {issue_id}")
    chroma_client.delete_item(id=issue_id)

    return Response(status_code=status.HTTP_204_NO_CONTENT)
