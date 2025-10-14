from huggingface_hub import InferenceClient
import logging
import inspect
import ast
from backend.tools.new_tools import AVAILABLE_TOOLS

class AgentOrchestrator:
    def __init__(self, api_key: str):
        self.logger = logging.getLogger(__name__)
        self.tools_code = self._get_tools_definitions()
        # Use a single model id consistently
        self.model_id = "meta-llama/Llama-3.1-8B-Instruct"
        self.router_client = InferenceClient(
            model=self.model_id,
            api_key=api_key)
        self.synthesizer_client = InferenceClient(
            model=self.model_id,
            api_key=api_key)

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
            if "(" not in call_part or not call_part.endswith(")"):
                return f"Error: Malformed call expression: {call_part}"
            func_name, args_part = call_part.split("(", 1)
            args_part = args_part[:-1]  # remove trailing )
            self.logger.info(f"Function: {func_name}, Args part: {args_part}")
            try:
                kwargs = self._parse_kwargs(args_part)
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
        # Parse a string like 'location="Holland, MI"' into a dict
        args_str = f"f({args_str})"  # fake function for parsing
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
            "You are a routing model. Decide if the user's query requires calling one of the provided tools. "
            "If a tool is needed, respond EXACTLY in the format: Call: tool_name(param_name=\"value\", ...). "
            "Check the conversation history: if the tool has already been called with the same arguments, respond with 'synthesizer' instead. "
            "After a tool has been called, respond with 'synthesizer' on the next turn. "
            "Do not add extra commentary."
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
                temperature=0.0  # deterministic routing
            )
            self.logger.info(f"Router raw response: {response}")
            decision = response.choices[0].message.content.strip()
            return decision
        except Exception as e:
            self.logger.error(f"Router model error: {e}")
            return "synthesizer"  # fallback to direct answer

    def _call_synthesizer_model(self, original_query: str, conversation_history: str):
        """Streams a synthesized final answer to the client."""
        system_message = (
            "You are a helpful assistant. Synthesize a concise, direct answer using any tool outputs provided. "
            "If tool outputs contain JSON, interpret them but do not just repeat raw JSON unless asked." )
        user_message = (
            f"Original User Query:\n{original_query}\n\nTool Execution History (may be empty):\n{conversation_history}\n\nProvide the best final answer now." )
        messages = [
            {"role": "system", "content": system_message},
            {"role": "user", "content": user_message}
        ]

        self.logger.info(f"Synthesizer messages: {messages}")
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
                    yield f"data: {content}\n\n"
            yield "data: [DONE]\n\n"
        except Exception as e:
            self.logger.error(f"Error during Synthesizer API call: {e}")
            yield f"data: Error: {str(e)}\n\n"
            yield "data: [DONE]\n\n"

    def process_query(self, query: str, max_steps: int = 5):
        self.logger.info(f"Processing query: {query}")
        conversational_history = f"User Query: {query}\n"
        last_tool_call = None

        for step in range(max_steps):
            self.logger.info(f"Step {step+1}/{max_steps}")
            action = self._call_router_model(conversational_history)
            self.logger.info(f"Router decision: {action}")
            if action.lower().startswith("call:"):
                self.logger.info(f"The last tool call was: {last_tool_call}, current action: {action}")
                if action == last_tool_call:
                    self.logger.warning("Detected repeated tool call; breaking to avoid loop.")
                    break
                tool_result = self._execute_tool_call(action)
                conversational_history += f"{action}\nTool output: {tool_result}\n"
                self.logger.info(f"Updated conversational history: {conversational_history}")
                last_tool_call = action
                continue
            else:
                final_response = self._call_synthesizer_model(query, conversational_history)
                self.logger.info("Final response generated by synthesizer.")
                return final_response
        # If loop ends without synthesizing, force synthesis
        self.logger.info("Reached max steps; forcing synthesis.")
        return self._call_synthesizer_model(query, conversational_history)
