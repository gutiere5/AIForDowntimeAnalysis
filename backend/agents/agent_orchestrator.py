import json
from huggingface_hub import InferenceClient
import logging
import inspect
import ast
from datetime import datetime
from backend.tools.tools import AVAILABLE_TOOLS
from backend.vector_chroma_db.chroma_client import ChromaClient
from backend.agents.request_context import RequestContext

class AgentOrchestrator:
    def __init__(self, api_key: str):
        self.logger = logging.getLogger(__name__)
        self.tools_code = self._get_tools_definitions()
        self.model_id = "meta-llama/Llama-3.1-8B-Instruct"
        self.router_client = InferenceClient(
            model=self.model_id,
            api_key=api_key)
        self.synthesizer_client = InferenceClient(
            model=self.model_id,
            api_key=api_key)
        self.conversation_db_client = ChromaClient(collection_name="conversations")

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
        self.logger.info(f"Executing tool call: {tool_call_string}")
        try:
            if "Call:" not in tool_call_string:
                return f"Error: Unrecognized tool call format: {tool_call_string}"

            call_part = tool_call_string.split("Call:", 1)[1].strip()
            self.logger.info(f"Parsed call part: {call_part}")

            # Robustly find the function name and arguments
            first_paren = call_part.find("(")
            last_paren = call_part.rfind(")")

            if first_paren == -1 or last_paren == -1 or last_paren < first_paren:
                return f"Error: Malformed call expression: {call_part}"

            func_name = call_part[:first_paren].strip()
            args_part = call_part[first_paren + 1:last_paren].strip()

            self.logger.info(f"Function: {func_name}, Args part: {args_part}")

            try:
                # Handle empty args case
                kwargs = self._parse_kwargs(args_part) if args_part else {}
            except Exception as e:
                return f"Error parsing arguments: {e}"

            if func_name in AVAILABLE_TOOLS:
                result = AVAILABLE_TOOLS[func_name](**kwargs)
                self.logger.info(f"Tool {func_name} executed with result: {result}")
                return result
            else:
                self.logger.error(f"Tool {func_name} not found in AVAILABLE_TOOLS.")
                return f"Error: Tool {func_name} not found."
        except Exception as e:
            self.logger.error(f"Error executing tool call: {e}")
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

    def _call_router_model(self, query: str) -> str:
        """Calls the routing model and returns its decision text.
        Output must be either:
          - Call: tool_name(arg1="value", ...)
          - synthesizer
        """
        system_instructions = (
            "You are a precise routing model. Your response MUST be one of two things: "
            "1. The word 'synthesizer'. "
            "2. A tool call formatted EXACTLY as: Call: tool_name(param_name=\"value\"). "
            "DO NOT add any other text, commentary, or newlines. "
            "If the user is asking about downtime, machine failures, or logs, call the `retrieve_log_entries` tool. "
            "Otherwise, or if the conversation is a simple greeting, respond with 'synthesizer'. "
            "After a tool has been called, you should typically respond with 'synthesizer' on the next turn so the main model can answer the user."
        )

        tools_context = f"Available tools:\n{self.tools_code}"
        user_content = f"{tools_context}\n\nUser query: {query}\nRespond with either a tool call or 'synthesizer'."
        messages = [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": user_content}
        ]

        self.logger.info(f"Router messages: {messages}")
        try:
            response = self.router_client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                max_tokens=128,
                temperature=0.7
            )
            self.logger.info(f"Router raw response: {response}")
            decision = response.choices[0].message.content.strip()
            return decision
        except Exception as e:
            self.logger.error(f"Router model error: {e}")
            return "synthesizer"

    def _call_synthesizer_model(self, original_query: str, conversation_history: str, conversation_id: str):
        """Streams a synthesized final answer to the client."""
        system_message = (
            "You are a helpful assistant. Your primary task is to answer user queries based on the provided tool outputs. "
            "When log entries are retrieved, use them as the source of truth for your answer. "
            "Synthesize a concise and direct answer from the log data. Format the information clearly, for example, using bullet points. "
            "If the tool output indicates no relevant logs were found, state that clearly to the user. "
            "Do not just repeat raw JSON; interpret and present the information in a user-friendly way."
        )
        user_message = (
            f"Original User Query:\n{original_query}\n\nTool Execution History (may be empty):\n{conversation_history}\n\nProvide the best final answer now." )
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]

        self.logger.info(f"Synthesizer messages: {messages}")
        accumulated_response = ""
        try:
            response = self.synthesizer_client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                max_tokens=250,
                temperature=0.7,
                stream=True
            )
            self.logger.info("Synthesizer streaming response initiated.")
            for chunk in response:
                try:
                    content = chunk.choices[0].delta.content
                except Exception:
                    content = None
                if content:
                    accumulated_response += content
                    payload = {"type": "chunk", "content": content}
                    self.logger.info(f"Synthesizer chunk: {payload}")
                    yield f"data: {json.dumps(payload)}\n\n"
            yield "data: {\"type\":\"done\"}\n\n"


        except Exception as e:
            self.logger.error(f"Error during Synthesizer API call: {e}")
            yield f"data: Error: {str(e)}\n\n"
            yield "data: [DONE]\n\n"

    def process_query(self, query: str, context: RequestContext, max_steps: int = 5):
        self.logger.info(f"Processing query: {query} for context: {context}")
        yield f"data: {json.dumps({'type': 'conversation_id', 'id': context.conversation_id})}\n\n"

        existing_conversation = self.conversation_db_client.get_conversation(context)
        if existing_conversation:
            conversational_history = existing_conversation["conversation_history"]
            metadata = existing_conversation["metadata"]
        else:
            conversational_history = f"User Query: {query}\n"
            metadata = {
                "initial_query": query, 
                "start_time": str(datetime.now()),
                "session_id": context.session_id
            }

        last_tool_call = None

        for step in range(max_steps):
            self.logger.info(f"Step {step+1}/{max_steps}")
            
            # Append the current query to the history for the router to see
            router_query = conversational_history + f"User Query: {query}\n"
            action = self._call_router_model(router_query).split('\n')[0].strip()
            
            self.logger.info(f"Router decision: {action}")
            if action.lower().startswith("call:"):
                self.logger.info(f"The last tool call was: {last_tool_call}, current action: {action}")
                if action == last_tool_call:
                    self.logger.warning("Detected repeated tool call; breaking to avoid loop.")
                    break
                tool_result = self._execute_tool_call(action)
                conversational_history += f"{action}\nTool output: {tool_result}\n"
                last_tool_call = action
                continue
            else:
                self.logger.info("Final response generated by synthesizer.")
                self.conversation_db_client.add_or_update_conversation(context, conversational_history, metadata)
                self.logger.info(f"Updated conversational history: {conversational_history}")
                yield from self._call_synthesizer_model(query, conversational_history, context.conversation_id)
                return
        self.logger.info("Reached max steps; forcing synthesis.")
        self.conversation_db_client.add_or_update_conversation(context, conversational_history, metadata)
        self.logger.info(f"Updated conversational history: {conversational_history}")
        yield from self._call_synthesizer_model(query, conversational_history, context.conversation_id)
