from backend.agents.llm_models.huggingface_inference_client import HuggingFaceInferenceService
from backend.repositories.sql_databases.conversations_repo import add_message
from backend.agents.utils.synthesizer_prompt import SYNTHESIZER_PROMPT_TEMPLATE
from backend.agents.utils.schemas import RequestContext
import logging
import json


class AgentSynthesis:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.llm_service = HuggingFaceInferenceService()

    def stream_final_response(self, query: str, data: dict, context: RequestContext):
        system_prompt = SYNTHESIZER_PROMPT_TEMPLATE

        synthesis_prompt = f"""
                A user asked: '{query}'
                The analysis found: {json.dumps(data)}
                """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": synthesis_prompt}
        ]

        self.logger.info(f"AgentSynthesizer: Synthesis messages for LLM:")
        accumulated_response = ""
        try:
            response = self.llm_service.create_completion(
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                stream=True,
            )

            self.logger.info("AgentSynthesizer: Streaming response initiated.")
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
            add_message(
                conversation_id=context.conversation_id,
                session_id=context.session_id,
                role='assistant',
                content=accumulated_response.strip()
            )
            self.logger.info(f"AgentSynthesizer: Final response generated: {accumulated_response}.")
        except Exception as e:
            self.logger.error(f"AgentSynthesizer Error: Failed to generate final response.")
            self.logger.error(f"AgentSynthesizer Error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
            yield "data: {\"type\":\"done\"}\n\n"
            return
