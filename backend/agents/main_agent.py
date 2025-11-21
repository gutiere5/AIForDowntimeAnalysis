from typing import Generator
import json
import logging
from backend.agents.utils.schemas import RequestContext
from backend.repositories.conversation_repo import conversations_repository
from backend.agents.agent_orchestrator2 import AgentOrchestrator
from backend.agents.agent_retrieval import AgentRetrieval
from backend.agents.agent_analysis import AgentAnalysis
from backend.agents.agent_synthesis import AgentSynthesis


class MainAgent:
    def __init__(self, name):
        self.logger = logging.getLogger(__name__)
        self.name = "MainAgent"
        self.agent_orchestrator = AgentOrchestrator()
        self.agent_retrieval = AgentRetrieval()
        self.agent_analysis = AgentAnalysis()
        self.agent_synthesizer = AgentSynthesis()
        self.current_data = None

    def process_query(self, query: str, context: RequestContext) -> Generator[str, None, None]:
        try:
            self.logger.info(f"{self.name}: processing query: {query} for context: {context}")
            self.logger.info(
                f"{self.name}: data: {json.dumps({'type': 'conversation_id', 'id': context.conversation_id})}")

            # Save the user's message immediately
            conversations_repository.add_message(context.conversation_id, context.session_id, 'user', query)

            # Retrieve conversation history
            conversation_history_list = conversations_repository.get_messages_by_conversation_id(
                context.conversation_id,
                context.session_id)

            # Get plan from orchestrator
            plan = self.agent_orchestrator.get_plan_from_orchestrator(query)

            if "error" in plan:
                yield f"data: {json.dumps({'type': 'error', 'message': plan['error']})}\n\n"
                return

            for i, step in enumerate(plan['steps']):
                agent_name = step.get('agent')
                task = step.get('task')
                self.logger.info(f"{self.name}: Starting step {i + 1} with agent {agent_name}")

                if agent_name == 'retrieval':
                    self.logger.info(f"{self.name}: Retrieval step with task: {task}")
                    self.current_data = self.agent_retrieval.retrieve_data(task)
                    if self.current_data and self.current_data.get('ids'):
                        self.logger.info(f"Agent Retrieval Found {len(self.current_data['ids'])} logs")
                        first_log = {'id': self.current_data['ids'][0], 'document': self.current_data['documents'][0],
                                     'metadata': self.current_data['metadatas'][0]}
                        self.logger.info(f"Agent Retrieval: Example of a log: {first_log}")

                elif agent_name == 'analysis':
                    self.current_data = self.agent_analysis.execute_analysis_task(task, self.current_data)
                    self.logger.info(f"Analysis Agent Result: {self.current_data}")

                elif agent_name == 'synthesis':
                    final_answer = self.agent_synthesizer.stream_final_response(query, self.current_data)
                    for chunk in final_answer:
                        yield chunk
        except Exception as e:
            self.logger.error(f"{self.name}: Error processing query: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': 'An error occurred while processing your query.'})}\n\n"
