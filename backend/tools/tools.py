import json
from .query_database import query_database as _query_database_impl
from .log_processor import log_to_text, generate_embedding
from .vector_db.chroma_client import ChromaClient
from .vector_retriever import VectorDBRetriever

AVAILABLE_TOOLS = {}

# Initialize ChromaClient and LogProcessor components
chroma_client_instance = ChromaClient(collection_name="log_embeddings")
vector_retriever_instance = VectorDBRetriever(collection_name="log_embeddings")

def register_tool(func):
    """Decorator to register a tool function."""
    AVAILABLE_TOOLS[func.__name__] = func
    return func

@register_tool
def get_weather_forecast(location: str) -> str:
    """
    Get the weather forecast for a specifi ed location.
    Args:
        location (str): The city and state, e.g., 'Holland, MI'.
    """
    if "holland, mi" in location.lower():
        return json.dumps({
            "location": "Holland, MI",
            "forecast": "Sunny",
            "high_temp": "75°F",
            "low_temp": "55°F",
            "humidity": "60%"
        })
    return json.dumps({
        "location": location,
        "forecast": "Data not available",
        "high_temp": "N/A",
        "low_temp": "N/A",
        "humidity": "N/A"
    })

@register_tool
def query_database(query: str) -> str:
    """
    Temporary registered tool wrapper for executing SELECT queries.
    Delegates to the implementation in `query_database.py` which currently returns mock data.
    """
    result = _query_database_impl(query)
    return json.dumps(result)

@register_tool
def retrieve_log_entries(query: str, top_k: int = 5) -> str:
    """
    Retrieves the top_k most relevant log entries from the vector database based on a natural language query.
    Args:
        query (str): The natural language query.
        top_k (int): The number of log entries to retrieve.
    """
    results = vector_retriever_instance.retrieve(query, top_k)
    return json.dumps(results)

@register_tool
def index_log_entry(log_entry_json: str) -> str:
    """
    Indexes a single log entry into the vector database.
    Args:
        log_entry_json (str): A JSON string representing the log entry.
                              Example: '{"id": 1, "timestamp": "2025-09-22 09:15:00", "machine_id": "M3", "reason_code": "SENSOR_FAIL", "duration_minutes": 25}'
    """
    try:
        log_entry_dict = json.loads(log_entry_json)
        text_representation = log_to_text(log_entry_dict)
        embedding = generate_embedding(text_representation)

        if embedding:
            chroma_client_instance.add_log_embedding(text_representation, embedding, metadata=log_entry_dict)
            return json.dumps({"status": "success", "message": "Log entry indexed successfully."})
        else:
            return json.dumps({"status": "error", "message": "Failed to generate embedding for log entry."})
    except json.JSONDecodeError:
        return json.dumps({"status": "error", "message": "Invalid JSON format for log_entry_json."})
    except Exception as e:
        return json.dumps({"status": "error", "message": f"An unexpected error occurred: {str(e)}"})