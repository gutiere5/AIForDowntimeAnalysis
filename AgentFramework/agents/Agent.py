from typing import List, Dict, Any
from openai import OpenAI
import json

class Agent:
    def __init__(self, api_key: str):
        self.name = "AI Agent"
        self.tools: List[Dict[str, Any]] = []
        self.conversation_history: List[Dict[str, str]] = []
        self.model = "gpt-4o-mini"
        self.openai_client = OpenAI(api_key=api_key)
        self.description = ("""You are an AI agent designed to assist users summarizing and answering questions.
        Follow these guidelines:
        1. Always respond in a concise and clear manner.
        3. Maintain a friendly and professional tone.
        4. Keep track of the conversation context to provide relevant answers.
        5. If you don't know the answer, admit it honestly.
        6. If a tool returns an error, apologize and explain the error to the user clearly.
        """)


    def add_tool(self, tool: Dict[str, Any]):
        self.tools.append(tool)

    def receive_message(self, message: str):
        self.conversation_history.append({"role": "user", "content": message})

    def generate_response(self) -> str:
        prompt = self._build_prompt()
        response = self.openai_client.chat.completions.create(
            model=self.model,
            messages=prompt,
            temperature=0.7,
            max_tokens=150
        )
        reply = response.choices[0].message['content']
        self.conversation_history.append({"role": "assistant", "content": reply})
        return reply

    def _build_prompt(self) -> List[Dict[str, str]]:
        system_message = {
            "role": "system",
            "content": f"You are {self.name}. {self.description} You have access to the following tools: {json.dumps(self.tools)}"
        }
        return [system_message] + self.conversation_history

    def get_conversation_history(self) -> List[Dict[str, str]]:
        return self.conversation_history