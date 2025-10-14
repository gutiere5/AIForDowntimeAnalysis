import json
from .query_database import query_database as _query_database_impl

AVAILABLE_TOOLS = {}

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