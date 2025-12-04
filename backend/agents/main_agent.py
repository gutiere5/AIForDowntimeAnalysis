import datetime
from typing import Generator
import json
import logging
from backend.agents.utils.schemas import RequestContext
from backend.agents.utils.date_converter import convert_dates_in_plan
from backend.repositories.sql_databases import conversations_repo
from backend.agents.agent_orchestrator import AgentOrchestrator
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
            conversations_repo.add_message(context.conversation_id, context.session_id, 'user', query)

            # Retrieve conversation history
            # conversation_history_list = conversations_repository.get_messages_by_conversation_id(
            #     context.conversation_id,
            #     context.session_id)

            # Get plan from orchestrator
            plan = self.agent_orchestrator.get_plan_from_orchestrator(query)
            self.logger.info(f"Plan from orchestrator: {plan}")

            if "error" in plan or not plan.get("steps"):
                self.logger.warning(f"Orchestrator failed to generate a valid plan. Falling back to synthesis.")
                fallback_data = {
                    "message": "I was unable to generate a structured plan to answer your query, but I will do my best to answer directly."
                }
                final_answer = self.agent_synthesizer.stream_final_response(query, fallback_data, context)
                for chunk in final_answer:
                    yield chunk
                return

            execution_datetime = datetime.datetime.now()
            plan = convert_dates_in_plan(plan, execution_datetime)
            self.logger.info(f"Plan after date conversion: {plan}")

            final_data_for_synthesis = {
                "known_issues": [],
                "downtime_logs": [],
            }
            last_retrieval_result = None

            for i, step in enumerate(plan['steps']):
                agent_name = step.get('agent')
                task = step.get('task')
                self.logger.info(f"{self.name}: Starting step {i + 1} with agent {agent_name}")

                try:
                    if agent_name == 'retrieval':
                        self.logger.info(f"{self.name}: Retrieval step with task: {task}")
                        retrieved_data = self.agent_retrieval.retrieve_data(task)
                        last_retrieval_result = retrieved_data

                        if retrieved_data and retrieved_data.get('documents') and retrieved_data['documents'][0]:
                            num_docs = len(retrieved_data['documents'][0])
                            self.logger.info(f"Agent Retrieval Found {num_docs} items.")

                            retrieved_items = [
                                {"document": doc, "metadata": meta, "id": doc_id}
                                for doc, meta, doc_id in zip(retrieved_data['documents'][0],
                                                              retrieved_data['metadatas'][0],
                                                              retrieved_data['ids'][0])
                            ]

                            if task.get('type') == 'known_issue_query':
                                final_data_for_synthesis['known_issues'].extend(retrieved_items)
                            else:
                                final_data_for_synthesis['downtime_logs'].extend(retrieved_items)

                            if retrieved_items:
                                self.logger.info(f"Example of a retrieved item: {retrieved_items[0]}")

                    elif agent_name == 'analysis':
                        if task.get('type') == 'passthrough':
                            self.logger.info("Skipping 'passthrough' analysis step as per new workflow.")
                        else:
                            analysis_result = self.agent_analysis.execute_analysis_task(task, last_retrieval_result)
                            final_data_for_synthesis.update(analysis_result)
                            self.logger.info(f"Analysis Agent Result: {analysis_result}")
                        self.logger.info(f"Cumulative Data for Synthesis: {final_data_for_synthesis}")


                    elif agent_name == 'synthesis':
                        final_answer = self.agent_synthesizer.stream_final_response(query, final_data_for_synthesis,
                                                                                    context)
                        for chunk in final_answer:
                            yield chunk
                        return

                    if last_retrieval_result and 'error' in last_retrieval_result:
                        self.logger.error(f"Error in step {i + 1} ({agent_name}): {last_retrieval_result['error']}")
                        final_data_for_synthesis['error'] = last_retrieval_result['error']
                        break

                except Exception as e:
                    self.logger.error(f"An unexpected error occurred in {agent_name} agent: {e}", exc_info=True)
                    final_data_for_synthesis = {"error": f"An unexpected error occurred in the {agent_name} agent."}
                    break

            # In case the loop finishes without a synthesis step (e.g., due to an error)
            if final_data_for_synthesis:
                final_answer = self.agent_synthesizer.stream_final_response(query, final_data_for_synthesis, context)
                for chunk in final_answer:
                    yield chunk

        except Exception as e:
            self.logger.error(f"{self.name}: Error processing query: {e}")
            yield f"data: {json.dumps({'type': 'error', 'message': 'An error occurred while processing your query.'})}\n\n"
