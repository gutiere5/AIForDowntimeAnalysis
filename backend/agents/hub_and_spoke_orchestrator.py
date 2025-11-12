from typing import Dict, Any, Generator
import json
import logging
from backend.agents.retrieval_agent import AgentRetrieval
from backend.agents.analysis_agent import AnalysisAgent
from backend.agents.synthesizer_agent import AgentSynthesizer
from backend.repositories.conversation_repo import conversations_repository
from backend.agents.schemas import RequestContext

# --- Orchestrator ---

class AgentOrchestrator:
    """
    Agent orchestrator that manages a sequence of agents
    to process a user query and return a final response.
    """
    def __init__(self, api_key: str):
        self.logger = logging.getLogger(__name__)
        self.retrieval_agent = AgentRetrieval(api_key=api_key)
        self.analysis_agent = AnalysisAgent(api_key=api_key)
        self.synthesis_agent = AgentSynthesizer(api_key=api_key)
        self.state: Dict[str, Any] = {}

    def process_query(self, query: str, context: RequestContext) -> Generator[str, None, None]:
        self.logger.info(f"Processing query: {query} for context: {context}")

        yield f"data: {json.dumps({'type': 'conversation_id', 'id': context.conversation_id})}\n\n"

        # Save the user's message immediately
        conversations_repository.add_message(context.conversation_id, context.session_id, 'user', query)

        # Retrieve conversation history
        history_list = conversations_repository.get_messages_by_conversation_id(context.conversation_id, context.session_id)

        # The retrieval_agent expects a List[Dict], so we pass history_list directly.
        self.logger.info("Orchestrator: Starting retrieval step.")
        retrieved_data = self.retrieval_agent.execute(history_list)
        self.state['retrieved_logs'] = retrieved_data
        self.logger.info(f"Orchestrator: Updated state with {len(retrieved_data)} retrieved logs.")
        yield f"data: {json.dumps({'type': 'status', 'message': f'Retrieved {len(retrieved_data)} log entries'})}\\n\\n"

        # Step: Analysis (Bypassed)
        yield f"data: {json.dumps({'type': 'status', 'message': 'Analysis bypassed.'})}\\n\\n"
        # analysis_result = self.analysis_agent.execute(self.state['retrieved_logs'])
        # self.state['analysis'] = analysis_result
        # self.logger.info(f"Orchestrator: Updated state with analysis: {analysis_result}")
        # yield f"data: {json.dumps({'type': 'status', 'message': 'Analysis complete'})}\\n\\n"

        # The synthesis_agent expects a dictionary, so we'll wrap the retrieved logs
        analysis_result = {'retrieved_logs': retrieved_data}
        self.state['analysis'] = analysis_result

        # Add the analyisis result to the converation history for context
        conversations_repository.add_message(context.conversation_id, context.session_id,'tool',  json.dumps(analysis_result))
        history_list = conversations_repository.get_messages_by_conversation_id(context.conversation_id, context.session_id)

        # Step: Synthesis
        yield f"data: {json.dumps({'type': 'status', 'message': 'Synthesizing response...'})}\\n\\n"
        final_response_content = ""
        for chunk in self.synthesis_agent.execute(conversational_history=history_list):
            try:
                # Extract content from chunk if it's a JSON string
                chunk_data = json.loads(chunk.split("data: ")[1])
                if chunk_data.get("type") == "chunk":
                    final_response_content += chunk_data.get("content", "")
            except (json.JSONDecodeError, IndexError):
                final_response_content += chunk
            yield chunk
        self.logger.info(f"Orchestrator: Final response synthesized.")
        yield f"data: {json.dumps({'type': 'status', 'message': 'Synthesis complete'})}\\n\\n"
        yield "data: {\"type\":\"done\"}\\n\\n"

        conversations_repository.add_message(context.conversation_id, context.session_id, 'assistant', final_response_content)
        self.logger.info(f"Saved assistant response to DB.")
