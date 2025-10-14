from typing import List, Dict
import logging
from huggingface_hub import InferenceClient


class AgentHuggingFace:
    def __init__(self, api_key: str):
        self.name = "Conversational Agent"
        self.model_id = "meta-llama/Llama-3.1-8B-Instruct"
        self.client = InferenceClient(
            model=self.model_id,
            api_key=api_key)
        self.conversation_history: List[Dict[str, str]] = []
        self.logger = logging.getLogger(__name__)
        self.description =  f"""You are designed to assist users with their queries."""


    def receive_message(self, message: str):
        self.conversation_history.append({"role": "user", "content": message})


    def generate_response(self):
        prompt = self._build_prompt()
        self.logger.info("Sending decision prompt to HuggingFace: %s", prompt)

        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=prompt,
                max_tokens=250,
                temperature=0.7,
                stream=True
            )

            full_response = ""
            for chunk in response:
                content = chunk.choices[0].delta.content
                if content is not None:
                    full_response += content
                    yield f"data: {content}\n\n"

            self.conversation_history.append({"role": "assistant", "content": full_response})
            yield "data: [DONE]\n\n"

        except Exception as e:
            self.logger.error(f"Error during HuggingFace API call: {e}")
            yield f"data: Error: {str(e)}\n\n"
            yield "data: [DONE]\n\n"



    def _build_prompt(self) -> List[Dict[str, str]]:
        system_message = {
            "role": "system",
            "content": f"You are a {self.name}. {self.description}"
        }
        return [system_message] + self.conversation_history



