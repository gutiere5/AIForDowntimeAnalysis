# backend/agents/trend_analysis.py
import numpy as np
from scipy import stats
import json

def analyze_trend(data: list, value_column: str, time_column: str = None) -> dict:
    """
    Analyzes data for statistical trends

    Args:
        data: List of dictionaries containing the data points
        value_column: The column name containing the values to analyze
        time_column: Optional column name for time series data

    Returns:
        Dictionary with trend analysis results
    """
    try:
        # Extract values
        if not data or len(data) < 2:
            return {
                "trend_detected": False,
                "summary": "Insufficient data points for trend analysis."
            }

        # Extract the values to analyze
        y_values = [float(item[value_column]) for item in data if value_column in item]

        # Use sequential indices if no time column specified
        x_values = range(len(y_values))
        if time_column:
            try:
                x_values = [float(item[time_column]) for item in data if time_column in item]
            except (ValueError, TypeError):
                # If time conversion fails, fall back to sequential indices
                x_values = range(len(y_values))

        # Perform linear regression
        slope, intercept, r_value, p_value, std_err = stats.linregress(x_values, y_values)

        # Determine if there's a statistically significant trend
        significant = p_value < 0.05
        r_squared = r_value ** 2

        # Generate descriptive summary
        direction = "upward" if slope > 0 else "downward"
        strength = "strong" if abs(r_value) > 0.7 else "moderate" if abs(r_value) > 0.4 else "weak"

        if significant:
            summary = f"A {strength} {direction} trend was detected with {r_squared:.2f} R-squared value."
        else:
            summary = "No statistically significant trend was found in the data."

        return {
            "trend_detected": significant,
            "slope": slope,
            "p_value": p_value,
            "r_squared": r_squared,
            "summary": summary
        }

    except Exception as e:
        return {
            "error": str(e),
            "trend_detected": False,
            "summary": f"Error during trend analysis: {str(e)}"
        }