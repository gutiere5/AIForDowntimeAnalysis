from backend.repositories.vector_chroma_db.chroma_client import ChromaClient
import logging


class AgentRetrieval:
    def __init__(self):
        self.downtime_logs_client = ChromaClient(collection_name="downtime_logs")
        self.known_issues_client = ChromaClient(collection_name="known_issues")
        self.logger = logging.getLogger(__name__)

    def retrieve_data(self, task):
        task_type = task.get('type')
        filters = task.get('filters', None)
        query_text = task.get('query_text')
        chroma_filters = filters if filters else None

        self.logger.info(
            f"AgentRetrieval: Retrieving data for task type '{task_type}' with query '{query_text}' and filters '{chroma_filters}'")

        if task_type == 'metadata_query':
            return self.downtime_logs_client.get_items(where=chroma_filters)

        elif task_type == 'known_issue_query':
            if not query_text:
                self.logger.error("AgentRetrieval: 'query_text' is required for 'known_issue_query'.")
                raise ValueError("'query_text' is required for 'known_issue_query'")
            return self.known_issues_client.query_items(query_texts=[query_text], n_results=3, where=chroma_filters)

        elif task_type == 'semantic_query':
            if not query_text:
                self.logger.error("AgentRetrieval: 'query_text' is required for 'semantic_query'.")
                raise ValueError("'query_text' is required for 'semantic_query'")
            return self.downtime_logs_client.query_items(query_texts=[query_text], n_results=10,
                                                          where=chroma_filters)

        elif task_type == 'hybrid_query':
            if not query_text:
                self.logger.error("AgentRetrieval: 'query_text' is required for 'hybrid_query'.")
                raise ValueError("'query_text' is required for 'hybrid_query'")
            return self.downtime_logs_client.query_items(query_texts=[query_text], n_results=5,
                                                          where=chroma_filters)
        else:
            self.logger.warning(f"AgentRetrieval: Unknown task type '{task_type}'")
            raise ValueError(f"Unknown task type: {task_type}")
