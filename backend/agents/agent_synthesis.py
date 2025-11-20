from backend.agents.llm_models.huggingface_inference_client import HuggingFaceInferenceService
import logging
import json


class AgentSynthesis:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.llm_service = HuggingFaceInferenceService()

    def stream_final_response(self, query, data):
        system_prompt = """
              You are an AI assistant specialized in summarizing technical analysis results.
              Your goal is to provide a clear, helpful answer to the user.
              You will be given the user's query and the JSON analysis data.

              ---
              RULES:

              1.  **If the analysis provides `top_causes`, `top_lines_by_downtime`, `top_downtimes`, or `most_frequent_downtimes`:**
                  * This is a summarization/analysis task.
                  * Directly answer the user's query (e.g., "The line with the most downtime was X" or "The most frequent cause was Y").
                  * Present the data as a clearly titled bulleted list.

              2.  **If the analysis provides `display_incidents` (a list of logs):**
                  * You must first determine the user's INTENT by looking at their original query.

                  * **INTENT 1: Diagnostic Query (e.g., "How do I fix...", "Why did...", "What is the solution...")**
                      * Your goal is to help the user solve their problem.
                      * First, look at the "note" field in the logs to find a pattern or solution.
                      * If you find a clear solution (e.g., "restarted the hmi"), state it as a potential fix.
                      * If not, state that there isn't enough information to propose a single solution.
                      * Then, present the logs as a bulleted list titled "Related Downtime Logs:".

                  * **INTENT 2: Retrieval Query (e.g., "Were there any...", "Show me...", "Find all...")**
                      * Your goal is to retrieve data. Do NOT propose a solution.
                      * If `entry_count` is 0, simply state "No logs were found matching your query."
                      * If `entry_count` is > 0, state: "Yes, I found {entry_count} logs."
                      * Then, present the logs as a bulleted list titled "Retrieved Logs:".
                      * Format the logs clearly (e.g., "• [minutes] minutes: '[note]' (Line: [line], [timestamp])").
              ---

              - Always state the units (e.g., "minutes", "hours").
              - Be concise and professional.
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
            self.logger.info(f"AgentSynthesizer: Final response generated: {accumulated_response}.")
        except Exception as e:
            self.logger.error(f"AgentSynthesizer Error: Failed to generate final response.")
            self.logger.error(f"AgentSynthesizer Error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'content': str(e)})}\n\n"
            yield "data: {\"type\":\"done\"}\n\n"
            return
