
from typing import List, Dict
import json
from backend.agents.llm_models.huggingface_inference_client import HuggingFaceInferenceService
import logging

logger = logging.getLogger(__name__)

class AnalysisAgent:
    """
    Agent responsible for analyzing data to find patterns and root causes.
    """
    def __init__(self, api_key: str):
        self.llm_service = HuggingFaceInferenceService(api_key=api_key)

    def execute(self, log_entries: List[str]) -> Dict[str, str]:
        """
        Analyzes log entries to find the root cause using an LLM.
        """
        logger.info(f"AnalysisAgent: Analyzing {len(log_entries)} log entries.")

        system_message = (
            "You are an expert in log analysis. Your task is to identify the root cause and significant patterns "
            "from a list of log entries. Provide your findings in a concise JSON format with 'root_cause' and 'pattern' keys."
        )
        user_message = f"Analyze the following log entries and identify the root cause and any significant patterns:\n\n{json.dumps(log_entries, indent=2)}\n\nProvide the output in JSON format: {{'root_cause': '...', 'pattern': '...'}}"

        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]

        try:
            response = self.llm_service.create_completion(
                messages=messages,
                max_tokens=500,
                temperature=0.7
            )
            analysis_text = response.choices[0].message.content.strip()
            logger.info(f"Analysis LLM raw response: {analysis_text}")

            # Attempt to parse the JSON response
            try:
                analysis_result = json.loads(analysis_text)
                if not isinstance(analysis_result, dict) or "root_cause" not in analysis_result or "pattern" not in analysis_result:
                    raise ValueError("LLM response is not a valid analysis dictionary.")
                return analysis_result
            except json.JSONDecodeError:
                logger.error(f"Analysis LLM did not return valid JSON: {analysis_text}")
                return {"root_cause": "unknown", "pattern": f"LLM response not valid JSON: {analysis_text}"}
            except ValueError as ve:
                logger.error(f"Analysis LLM response format error: {ve}")
                return {"root_cause": "unknown", "pattern": f"LLM response format error: {ve}"}

        except Exception as e:
            logger.error(f"Error during Analysis API call: {e}")
            return {"root_cause": "error", "pattern": f"Error during analysis: {e}"}

