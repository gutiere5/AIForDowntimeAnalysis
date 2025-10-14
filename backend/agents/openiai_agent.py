from typing import List, Dict, Any
from openai import OpenAI
import json
import logging
from backend.tools.query_database import query_database
from backend.tools.trend_analysis import analyze_trend

class AgentOpenAI:
    def __init__(self, api_key: str):
        self.name = "Conversational Agent"
        self.tools: List[Dict[str, Any]] = []
        self.tool_functions = {
            "query_database": query_database,
            "analyze_trend": analyze_trend
        }
        self.conversation_history: List[Dict[str, str]] = []
        self.model = "gpt-4o-mini"
        self.openai_client = OpenAI(api_key=api_key)
        self.logger = logging.getLogger(__name__)
        self.description = f"""You are designed to assist users with their queries.
        Core guidelines:
        1. Analyze each query to determine if external data is needed - only use tools when necessary
        2. When database access is required, use ONLY SELECT statements with the query_database tool
        3. If a query can be answered without database access, respond directly
        4. When users ask about trends or patterns in data, first query the database, then analyze the data using the analyze_trend tool
        5. After receiving data, provide a concise, helpful response that includes trend analysis results when applicable
        6. Be friendly and professional
        7. If you don't know something, admit it honestly
        8. Clearly explain any errors that occur during tool use
        Remember: Only use the database when needed, and never use INSERT, UPDATE, DELETE or other modifying SQL statements.
        """

    def add_tool(self, tool: Dict[str, Any]):
        self.tools.append(tool)

    def receive_message(self, message: str):
        self.conversation_history.append({"role": "user", "content": message})

    def get_conversation_history(self) -> List[Dict[str, str]]:
        return self.conversation_history

    def generate_response(self):
        prompt = self._build_prompt()
        self.logger.debug("Sending decision prompt to OpenAI: %s", json.dumps(prompt, indent=2))

        decision_response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=prompt,
            tools=self.tools if self.tools else None,
            tool_choice="auto" if self.tools else None,
            temperature=0.7
        )

        decision_message = decision_response.choices[0].message
        tool_calls = decision_message.tool_calls if hasattr(decision_message, "tool_calls") else None

        self._add_assistant_message_to_history(decision_message)

        if tool_calls:
            self._process_tool_calls(tool_calls)

        final_prompt = self._build_prompt()
        self._log_printable_prompt(final_prompt)

        return self._stream_final_response(final_prompt)

    def _build_prompt(self) -> List[Dict[str, str]]:
        system_message = {
            "role": "system",
            "content": f"You are {self.name}. {self.description} You have access to the following tools: {json.dumps(self.tools)}"
        }
        return [system_message] + self.conversation_history

    def _add_assistant_message_to_history(self, decision_message):
        self.conversation_history.append({
            "role": "assistant",
            "content": decision_message.content or "",
            "tool_calls": [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                } for tool_call in decision_message.tool_calls
            ] if decision_message.tool_calls else None
        })

    def _process_tool_calls(self, tool_calls):
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            tool_to_call = next((tool for tool in self.tools if tool["function"]["name"] == function_name), None)
            if not tool_to_call:
                self._handle_missing_tool(tool_call.id, function_name)
                continue

            result_content = self._execute_tool(function_name, function_args, tool_call.id)

            self.conversation_history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": result_content
            })

    def _handle_missing_tool(self, tool_call_id, function_name):
        error_msg = f"Tool {function_name} not found"
        self.conversation_history.append({
            "role": "tool",
            "tool_call_id": tool_call_id,
            "name": function_name,
            "content": json.dumps({"error": error_msg})
        })

    def _execute_tool(self, function_name, function_args, tool_call_id):
        if function_name in self.tool_functions:
            if function_name == "query_database":
                result = self.tool_functions[function_name](function_args.get("query", ""))
            elif function_name == "analyze_trend":
                result = self.tool_functions[function_name](
                    data=function_args.get("data", []),
                    value_column=function_args.get("value_column", ""),
                    time_column=function_args.get("time_column")
                )
            else:
                result = self.tool_functions[function_name](**function_args)

            return json.dumps(result)
        else:
            return json.dumps({"error": f"Implementation for tool '{function_name}' not found"})

    def _log_printable_prompt(self, prompt):
        printable_prompt = [
            {k: v for k, v in msg.items() if k != "tool_calls"}
            if isinstance(msg, dict) and "tool_calls" in msg else msg
            for msg in prompt
        ]
        self.logger.debug("Sending final prompt to OpenAI: %s", json.dumps(printable_prompt, indent=2))

    def _stream_final_response(self, final_prompt):
        stream = self.openai_client.chat.completions.create(
            model=self.model,
            messages=final_prompt,
            temperature=0.7,
            stream=True
        )

        full_response = ""
        for chunk in stream:
            content = chunk.choices[0].delta.content or ""
            if content:
                full_response += content
                yield f"data: {content}\n\n"

        self.conversation_history.append({"role": "assistant", "content": full_response})
        yield "data: [DONE]\n\n"