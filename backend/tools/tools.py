import json
from .vector_retriever import VectorDBRetriever

AVAILABLE_TOOLS = {}

vector_retriever_instance = VectorDBRetriever(collection_name="log_embeddings")

def register_tool(func):
    """Decorator to register a tool function."""
    AVAILABLE_TOOLS[func.__name__] = func
    return func

@register_tool
def retrieve_log_entries(query: str, top_k: int = 15) -> str:
    """
    Retrieves the top_k most relevant log entries from the vector database based on a natural language query.
    Args:
        query (str): The natural language query.
        top_k (int): The number of log entries to retrieve.
    """
    results = vector_retriever_instance.retrieve(query, top_k)
    return json.dumps(results)
