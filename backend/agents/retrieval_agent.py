from typing import List, Dict, Any
import json
import logging
from backend.agents.llm_models.huggingface_inference_client import HuggingFaceInferenceService
from backend.agents.tools.tools import AVAILABLE_TOOLS, TOOL_SCHEMA_DEFINITIONS
from backend.agents.schemas import ConversationHistory, ChatMessage
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class AgentRetrieval:
    """
    Agent responsible for retrieving raw data based on a query using structured tool calls.
    """
    def __init__(self, api_key: str):
        self.llm_service = HuggingFaceInferenceService(api_key=api_key)

    def execute(self, conversational_history: List[Dict[str, str]]) -> List[str]:
        """
        Retrieves relevant log entries based on a natural language query using an LLM to generate structured tool calls.
        """
        query = conversational_history[-1]['content'] if conversational_history and conversational_history[-1]['role'] == 'user' else "no query found"
        logger.info(f"AgentRetrieval: Searching for logs related to '{query}' with history.")

        system_instructions = (
            "You are a precise routing model. Your main goal is to execute the tool for retrieving vector logs based on the user's query. "
            "You are also in charge of retrieving the correct amount of logs, especially for downtime log analysis. "
            "You MUST call the `retrieve_log_entries` tool to get relevant log entries."
        )

        messages = [
            {"role": "system", "content": system_instructions}
        ]

        try:
            # Validate and extend with conversation history
            validated_history = ConversationHistory(messages=[ChatMessage(**msg) for msg in conversational_history])
            messages.extend(validated_history.to_list())
        except ValidationError as e:
            logger.error(f"Invalid conversation history structure: {e}")
            return [f"Error: Invalid conversation history format provided to retrieval agent."]

        logger.info(f"Retrieval Agent messages for LLM: {messages}")
        try:
            response = self.llm_service.create_completion(
                messages=messages,
                max_tokens=128,
                temperature=0.7,
                tools=TOOL_SCHEMA_DEFINITIONS # Pass the structured tool definitions
            )
            logger.info(f"Retrieval Agent raw response: {response}")

            # Check if the model decided to call a tool
            tool_calls = response.choices[0].message.tool_calls
            if tool_calls:
                # Assuming only one tool call for simplicity in this context
                tool_call = tool_calls[0]
                func_name = tool_call.function.name
                func_args = json.loads(tool_call.function.arguments)

                if func_name in AVAILABLE_TOOLS:
                    logger.info(f"Executing tool: {func_name} with args: {func_args}")
                    result = AVAILABLE_TOOLS[func_name](**func_args)
                    logger.info(f"Tool {func_name} executed with result (truncated): {result[:200]}...")
                    return json.loads(result) # Assuming tool returns JSON string
                else:
                    logger.error(f"Tool {func_name} not found in AVAILABLE_TOOLS.")
                    return [f"Error: Tool {func_name} not found."]
            else:
                logger.warning("LLM did not make a tool call. Responding with default error.")
                return [f"Error: The model did not make a tool call. Please rephrase your query to ask for log entries."]

        except Exception as e:
            logger.error(f"Error in AgentRetrieval execution: {e}")
            return [f"Error retrieving logs: {e}"]
