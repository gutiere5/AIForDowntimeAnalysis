from backend.repositories.vector_chroma_db.chroma_client import ChromaClient
from sentence_transformers import SentenceTransformer
import logging

class AgentRetrieval:
    def __init__(self):
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.chroma_client = ChromaClient(collection_name="downtime_logs")
        self.logger = logging.getLogger(__name__)

    def retrieve_data(self, task):
        task_type = task.get('type')
        filters = task.get('filters', None)
        query_text = task.get('query_text')
        chroma_filters = filters if filters else None # TODO refactor this later, improve since it was a bug

        self.logger.info(f"AgentRetrieval: Retrieving data for task type '{task_type}' with query '{query_text}' and filters '{chroma_filters}'")

        if task_type == 'metadata_query':
            return self.chroma_client.get_logs(where=chroma_filters)

        elif task_type == 'semantic_query':
            query_embedding = self.embedding_model.encode(query_text).tolist()
            return self.chroma_client.query_logs(query_embeddings=[query_embedding], n_results=10, where=chroma_filters)

        elif task_type == 'hybrid_query':
            query_embedding = self.embedding_model.encode(query_text).tolist()
            return self.chroma_client.query_logs(query_embeddings=[query_embedding], n_results=10, where=chroma_filters)

        else:
            return {"error": f"Unknown task type: {task_type}"}
