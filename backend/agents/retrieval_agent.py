from typing import List, Dict
import json
import inspect
import ast
from backend.agents.llm_models.huggingface_inference_client import HuggingFaceInferenceService
import logging
from backend.agents.tools.tools import AVAILABLE_TOOLS
from backend.agents.schemas import ConversationHistory, ChatMessage
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class AgentRetrieval:
    """
    Agent responsible for retrieving raw data based on a query.
    """
    def __init__(self, api_key: str):
        self.llm_service = HuggingFaceInferenceService(api_key=api_key)
        self.tools_code = self._get_tools_definitions()

    def _get_tools_definitions(self):
        """Gets the signature and docstrings for all registered tools (for prompt context only)."""
        code_strings = []
        for func in AVAILABLE_TOOLS.values():
            signature = inspect.signature(func)
            docstring = inspect.getdoc(func) or ""
            # Provide a lightweight pseudo-definition for the model to reason about
            code_strings.append(f"def {func.__name__}{signature}:\n    \"\"\"{docstring}\"\"\"")
        return "\n\n".join(code_strings)

    def _execute_tool_call(self, tool_call_string: str):
        logger.info(f"Executing tool call: {tool_call_string}")
        try:
            if "Call:" not in tool_call_string:
                return f"Error: Unrecognized tool call format: {tool_call_string}"

            call_part = tool_call_string.split("Call:", 1)[1].strip()
            logger.info(f"Parsed call part: {call_part}")

            # Robustly find the function name and arguments
            first_paren = call_part.find("(")
            last_paren = call_part.rfind(")")

            if first_paren == -1 or last_paren == -1 or last_paren < first_paren:
                return f"Error: Malformed call expression: {call_part}"

            func_name = call_part[:first_paren].strip()
            args_part = call_part[first_paren + 1:last_paren].strip()

            logger.info(f"Function: {func_name}, Args part: {args_part}")

            try:
                # Handle empty args case
                kwargs = self._parse_kwargs(args_part) if args_part else {}
            except Exception as e:
                return f"Error parsing arguments: {e}"

            if func_name in AVAILABLE_TOOLS:
                result = AVAILABLE_TOOLS[func_name](**kwargs)
                logger.info(f"Tool {func_name} executed with result: {result}")
                return result
            else:
                logger.error(f"Tool {func_name} not found in AVAILABLE_TOOLS.")
                return f"Error: Tool {func_name} not found."
        except Exception as e:
            logger.error(f"Error executing tool call: {e}")
            return f"Error executing tool call: {e}"

    def _parse_kwargs(self, args_str):
        args_str = f"f({args_str})"
        node = ast.parse(args_str, mode="eval")
        call = node.body
        if not isinstance(call, ast.Call):
            raise ValueError("Malformed call")
        kwargs = {}
        for kw in call.keywords:
            kwargs[kw.arg] = ast.literal_eval(kw.value)
        return kwargs

    def _build_message_history(self, conversational_history: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Builds the message history for the LLM, following the standard format of a list of dictionaries,
        each with a "role" and "content" key. This is a common pattern for conversational models.

        Example of the structure:
        [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is the weather today?"},
            {"role": "assistant", "content": "It is sunny."}
        ]
        """
        system_instructions = (
            "You are a precise routing model. Your main goal is to execute the tool for retrieving vector logs based on the user's query. "
            "You are also in charge of retrieving the correct amount of logs, especially for downtime log analysis. "
            "Your response MUST be a tool call formatted EXACTLY as: Call: tool_name(param_name=\"value\"). "
            "DO NOT add any other text, commentary, or newlines. "
            "You MUST call the `retrieve_log_entries` tool to get relevant log entries.\n\n"
            f"Available tools:\n{self.tools_code}"
        )

        messages = [
            {"role": "system", "content": system_instructions}
        ]

        try:
            # Validate the incoming history
            validated_history = ConversationHistory(messages=[ChatMessage(**msg) for msg in conversational_history])
            messages.extend(validated_history.to_list())
            # Add a specific instruction for the tool call
            messages.append({"role": "user", "content": "Respond with a tool call."})
        except ValidationError as e:
            logger.error(f"Invalid conversation history structure: {e}")
            # Handle the error, maybe by returning an empty history or raising an exception
            pass
        return messages

    def execute(self, conversational_history: List[Dict[str, str]]) -> List[str]:
        """
        Retrieves relevant log entries based on a natural language query using an LLM to generate tool calls.
        """
        query = conversational_history[-1]['content'] if conversational_history and conversational_history[-1]['role'] == 'user' else "no query found"
        logger.info(f"AgentRetrieval: Searching for logs related to '{query}' with history.")

        messages = self._build_message_history(conversational_history)

        logger.info(f"Retrieval Router messages: {messages}")
        try:
            response = self.llm_service.create_completion(
                messages=messages,
                max_tokens=128,
                temperature=0.7
            )
            logger.info(f"Retrieval Router raw response: {response}")
            decision = response.choices[0].message.content.strip()

            tool_result = self._execute_tool_call(decision)
            # Assuming tool_result is a JSON string of a list of log entries
            return json.loads(tool_result)
        except Exception as e:
            logger.error(f"Error in AgentRetrieval: {e}")
            return [f"Error retrieving logs: {e}"]

#TODO : Figure out the tool call can parse and executed in a more robust way
