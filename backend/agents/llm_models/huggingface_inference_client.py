from typing import List, Dict, Generator, Any, Union
from huggingface_hub import InferenceClient
import logging
import os
from dotenv import load_dotenv

def get_api_key():
    load_dotenv()
    token = os.getenv("HUGGINGFACE_API_TOKEN")
    if not token:
        raise ValueError("HUGGINGFACE_API_TOKEN not found in environment variables.")
    return token


class HuggingFaceInferenceService:
    """
    A wrapper for the Hugging Face InferenceClient to standardize LLM calls.
    """
    def __init__(self, model_id: str = "meta-llama/Llama-3.1-8B-Instruct"):
        self.model_id = model_id
        self.logger = logging.getLogger(__name__)
        self.api_key = get_api_key()
        try:
            self.client = InferenceClient(model=self.model_id, api_key=self.api_key)
            self.logger.info(f"InferenceClient initialized for model: {self.model_id}")
        except Exception as e:
            self.logger.error(f"Failed to initialize InferenceClient: {e}")
            raise

    def create_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
        response_format: dict = None,
        stream: bool = False,
    ) -> Union[Generator[Any, None, None], Any]:
        """
        Creates a chat completion using the configured model.
        Can handle both streaming and non-streaming responses.
        """
        self.logger.info(f"Creating completion with model {self.model_id}, stream={stream}")
        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                response_format=response_format,
                stream=stream,
            )
            return response
        except Exception as e:
            self.logger.error(f"Error during chat completion API call: {e}")
            if stream:
                return (i for i in [])
            raise
