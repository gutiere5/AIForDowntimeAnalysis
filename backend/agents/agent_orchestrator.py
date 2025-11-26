from backend.agents.llm_models.huggingface_inference_client import HuggingFaceInferenceService
from backend.agents.utils.orchestrator_prompt import ORCHESTRATOR_PROMPT_TEMPLATE, EXAMPLES, PLAN_SCHEMA
from typing import Dict, Any
import logging
import json
import re
import datetime


class AgentOrchestrator:
    def __init__(self):
        self.llm_service = HuggingFaceInferenceService()
        self.logger = logging.getLogger(__name__)

    def get_plan_from_orchestrator(self, user_query: str) -> Dict[str, Any]:
        self.logger.info(f"Getting plan for user query: {user_query}.")
        now = datetime.datetime.now()

        system_instructions = ORCHESTRATOR_PROMPT_TEMPLATE.format(current_date_iso=now.isoformat())

        response = None
        try:
            messages = [{"role": "system", "content": system_instructions}]
            messages.extend(EXAMPLES)
            messages.append({"role": "user", "content": user_query})

            response = self.llm_service.create_completion(
                messages=messages,
                max_tokens=1024,
                temperature=0.01,
                response_format={
                    "type": "json_object",
                    "schema": PLAN_SCHEMA
                }
            )

            json_str = response.choices[0].message.content.strip()
            json_str = response.choices[0].message.content.strip()

            if "```" in json_str:
                json_str = json_str.replace("```json", "").replace("```", "")

            json_str = re.sub(r'\s+', ' ', json_str).strip()
            plan = json.loads(json_str)
            json_str = re.sub(r'\s+', ' ', json_str).strip()
            plan = json.loads(json_str)
            self.logger.info(f"Orchestrator Generated Plan: {plan}")

            return plan
        except Exception as e:
            self.logger.error(f"Orchestrator Error: Failed to generate plan.")
            self.logger.error(f"Orchestrator Error: {e}")
            self.logger.error(f"Raw Response: {response}")
            return {"error": "Failed to generate a valid plan."}


if __name__ == "__main__":
    orchestrator = AgentOrchestrator()
    user_query = "Schedule maintenance for machine M2 next week."
    plan = orchestrator.get_plan_from_orchestrator(user_query)
    print("Generated Plan:")
    print(json.dumps(plan, indent=2))
