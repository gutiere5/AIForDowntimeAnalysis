from typing import Generator
import json
import logging
import pandas as pd
from backend.agents.utils.schemas import RequestContext
from backend.agents.utils.date_converter import convert_dates_in_plan
from backend.repositories.sql_databases import conversations_repo
from backend.agents.agent_orchestrator import AgentOrchestrator
from backend.agents.agent_retrieval import AgentRetrieval
from backend.agents.agent_analysis import AgentAnalysis
from backend.agents.agent_synthesis import AgentSynthesis


class MainAgent:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.name = "MainAgent"
        self.agent_orchestrator = AgentOrchestrator()
        self.agent_retrieval = AgentRetrieval()
        self.agent_analysis = AgentAnalysis()
        self.agent_synthesizer = AgentSynthesis()

    def process_query(self, query: str, context: RequestContext) -> Generator[str, None, None]:
        agent_name_in_error = None
        analysis_for_synthesis = {}
        retrieved_data = pd.DataFrame()
        limited_conversation_history = []
        try:
            self.logger.info(f"{self.name}: processing query: {query} for context: {context}")
            self.logger.info(f"{self.name}: data: {json.dumps({'type': 'conversation_id', 'id': context.conversation_id})}")

            conversations_repo.add_message(context.conversation_id, context.session_id, 'user', query)

            conversation_history_list = conversations_repo.get_messages_by_conversation_id(
                context.conversation_id,
                context.session_id)
            limited_conversation_history = conversation_history_list[-25:]

            plan = self.agent_orchestrator.get_plan_from_orchestrator(query, limited_conversation_history)
            self.logger.info(f"Plan from orchestrator: {plan}")

            plan = convert_dates_in_plan(plan)
            self.logger.info(f"Plan after date conversion: {plan}")
            for i, step in enumerate(plan['steps']):
                agent_name = step.get('agent')
                agent_name_in_error = agent_name
                task = step.get('task')
                self.logger.info(f"{self.name}: Starting step {i + 1} with agent {agent_name}")

                if agent_name == 'retrieval':
                    self.logger.info(f"Retrieval step with task: {task}")
                    retrieved_data = self.agent_retrieval.retrieve_data(task)
                    self.logger.info(f"Agent Retrieval data: {retrieved_data}")

                elif agent_name == 'analysis':
                    analysis_result = self.agent_analysis.execute_analysis_task(task, retrieved_data)
                    analysis_for_synthesis.update(analysis_result)
                    self.logger.info(f"Analysis Agent Result: {analysis_result}")
                    self.logger.info(f"Final Data for Synthesis: {analysis_for_synthesis}")

                elif agent_name == 'synthesis':
                    synthesis_data = analysis_for_synthesis
                    if task:
                        synthesis_data.update(task)
                    final_answer = self.agent_synthesizer.stream_final_response(query, synthesis_data,
                                                                                context, limited_conversation_history)
                    for chunk in final_answer:
                        yield chunk
                    return
                agent_name_in_error = None
        except Exception as e:
            if agent_name_in_error:
                self.logger.error(f"An unexpected error occurred in {agent_name_in_error} agent: {e}", exc_info=True)
                analysis_for_synthesis['error'] = f"An unexpected error occurred in the {agent_name_in_error} agent."
                final_answer = self.agent_synthesizer.stream_final_response(query, analysis_for_synthesis, context,
                                                                            limited_conversation_history)
                for chunk in final_answer:
                    yield chunk
            else:
                self.logger.error(f"{self.name}: Error processing query: {e}", exc_info=True)
                yield f"data: {json.dumps({'type': 'error', 'message': 'An error occurred while processing your query.'})}\n\n"
