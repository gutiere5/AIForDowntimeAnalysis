from typing import Dict, Generator, List
import json
from backend.agents.llm_models.huggingface_inference_client import HuggingFaceInferenceService
import logging
from backend.agents.schemas import ConversationHistory, ChatMessage
from pydantic import ValidationError

logger = logging.getLogger(__name__)

class AgentSynthesizer:
    """
    Agent responsible for creating a human-readable response from analysis.
    """
    def __init__(self, api_key: str):
        self.llm_service = HuggingFaceInferenceService(api_key=api_key)

    def execute(self, conversational_history: List[Dict[str, str]]) -> Generator[str, None, None]:
        """
        Synthesizes a final response from the analysis using an LLM, yielding chunks.
        """
        logger.info(f"AgentSynthesizer: Synthesizing response from history.")

        system_message = (
            "You are a helpful assistant. Your primary task is to answer user queries based on the provided analysis and conversation history. "
            "Synthesize a concise and direct answer from the analysis data, taking into account the flow of the conversation. "
            "Format the information clearly, for example, using bullet points. "
            "Do not just repeat raw JSON; interpret and present the information in a user-friendly way."
        )
        
        messages = [
            {"role": "system", "content": system_message}
        ]

        try:
            # Validate the incoming history
            validated_history = ConversationHistory(messages=[ChatMessage(**msg) for msg in conversational_history])
            messages.extend(validated_history.to_list())
        except ValidationError as e:
            logger.error(f"Invalid conversation history structure in Synthesizer: {e}")
            # Proceed with only the system message if history is invalid
            pass

        # The last message should be the analysis from the 'tool'
        if messages[-1]["role"] == "tool":
             messages[-1]["content"] += "\n\nBased on this analysis and the conversation history, provide a final answer."
        else:
            # Handle case where there is no analysis
            messages.append({
                "role": "user",
                "content": "There was no analysis provided. Please inform the user that you couldn't retrieve any information."
            })

        accumulated_response = ""
        try:
            response = self.llm_service.create_completion(
                messages=messages,
                max_tokens=250,
                temperature=0.7,
                stream=True
            )
            logger.info("Synthesizer streaming response initiated.")
            for chunk in response:
                try:
                    content = chunk.choices[0].delta.content
                except Exception:
                    content = None
                if content:
                    accumulated_response += content
                    payload = {"type": "chunk", "content": content}
                    yield f"data: {json.dumps(payload)}\n\n"
            yield "data: {\"type\":\"done\"}\n\n"
        except Exception as e:
            logger.error(f"Error during Synthesizer API call: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
            yield "data: {\"type\":\"done\"}\n\n"
