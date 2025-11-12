from typing import List, Dict, Generator, Any, Union
from huggingface_hub import InferenceClient
import logging

logger = logging.getLogger(__name__)

class HuggingFaceInferenceService:
    """
    A wrapper for the Hugging Face InferenceClient to standardize LLM calls.
    """
    def __init__(self, api_key: str, model_id: str = "meta-llama/Llama-3.1-8B-Instruct"):
        self.model_id = model_id
        try:
            self.client = InferenceClient(model=self.model_id, api_key=api_key)
            logger.info(f"InferenceClient initialized for model: {self.model_id}")
        except Exception as e:
            logger.error(f"Failed to initialize InferenceClient: {e}")
            raise

    def create_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int,
        temperature: float,
        stream: bool = False
    ) -> Union[Generator[Any, None, None], Any]:
        """
        Creates a chat completion using the configured model.
        Can handle both streaming and non-streaming responses.
        """
        logger.debug(f"Creating completion with model {self.model_id}, stream={stream}")
        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                stream=stream
            )
            return response
        except Exception as e:
            logger.error(f"Error during chat completion API call: {e}")
            if stream:
                return (i for i in [])  # Return an empty generator
            raise
