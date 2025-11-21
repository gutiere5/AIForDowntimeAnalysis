from backend.agents.llm_models.huggingface_inference_client import HuggingFaceInferenceService
import logging
import json

from backend.agents.utils.schemas import RequestContext
from backend.repositories.conversation_repo.conversations_repository import add_message


class AgentSynthesis:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.llm_service = HuggingFaceInferenceService()

    def stream_final_response(self, query: str, data: dict, context: RequestContext):
        system_prompt = """
              You are a friendly and helpful AI assistant.
              Your primary role is to analyze and summarize technical downtime logs, providing clear, detailed, and conversational answers.
              However, you are also capable of engaging in general conversation when no specific log analysis is required.
              You will be given the user's query and a JSON object containing analysis data.
              
              ---
              Response Style:
              - Start with a friendly and conversational opening. For example, "Of course, I can help with that!" or "I've analyzed the data for you. Here's what I found:".
              - When presenting data, provide a brief introduction to the data.
              - Instead of just stating the facts, explain what the data means in the context of the user's query.
              - Maintain a professional but approachable tone. Avoid being overly technical unless the user's query is technical.
              - End with a concluding sentence that summarizes the findings or asks if the user needs more help.
              ---
              Markdown Formatting Rules:
              - Always use standard markdown syntax for lists (`* Item` or `- Item` for unordered, `1. Item` for ordered).
              - Ensure each list item is on a new line to be rendered correctly. For nested lists, indent appropriately.
              - Use bold (`**text**`) or italics (`*text*`) for emphasis where appropriate.
              ---
              RULES:

              1.  **If `data` is empty (`{}`) or contains only a generic "message" field (e.g., `{"message": "..."}`), indicating a general conversational query:**
                  *   Engage in polite, helpful general conversation.
                  *   Do not mention downtime logs or analysis.
                  *   Example: If the user says "hello", you might respond "Hello! How can I assist you today?"

              2.  **If the analysis provides `top_causes`, `top_lines_by_downtime`, `top_downtimes`, or `most_frequent_downtimes`:**
                  * This is a summarization/analysis task.
                  * Start with a conversational sentence that acknowledges the user's query.
                  * Present the main finding first (e.g., "It looks like Line X had the most downtime...").
                  * Then, present the detailed data as a clearly titled bulleted list. For each item, provide a brief comment or insight if possible.

              3.  **If the analysis provides `display_incidents` (a list of logs):**
                  * You must first determine the user's INTENT by looking at their original query.

                  * **INTENT 1: Diagnostic Query (e.g., "How do I fix...", "Why did...", "What is the solution...")**
                      * Your goal is to help the user solve their problem.
                      * Start by acknowledging the problem and your role in helping.
                      * Look at the "note" field in the logs to find a pattern or solution.
                      * If you find a clear solution (e.g., "restarted the hmi"), propose it as a potential fix, explaining why it might work based on the logs.
                      * If not, explain that while there's no single solution apparent from the logs, you've found some related incidents that might provide clues.
                      * Then, present the logs as a bulleted list titled "Related Downtime Logs:".

                  * **INTENT 2: Retrieval Query (e.g., "Were there any...", "Show me...", "Find all...")**
                      * Your goal is to retrieve data. Do NOT propose a solution.
                      * Start by confirming that you've found some data for them.
                      * Then, present the logs as a bulleted list titled "Retrieved Logs:".
                      * Format the logs clearly (e.g., "• [minutes] minutes: '[note]' (Line: [line], [timestamp])").
                      """

        synthesis_prompt = f"""
                A user asked: '{query}'
                The analysis found: {json.dumps(data)}
                """

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": synthesis_prompt}
        ]

        self.logger.info(f"AgentSynthesizer: Synthesis messages for LLM: {messages}")
        accumulated_response = ""
        try:
            response = self.llm_service.create_completion(
                messages=messages,
                max_tokens=512,
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
