from backend.agents.llm_models.embedding_model import EMBEDDING_MODEL
from backend.repositories.vector_chroma_db.chroma_client import ChromaClient

class VectorDBRetriever:
    def __init__(self, collection_name="log_embeddings"):
        self.embedding_model = EMBEDDING_MODEL
        self.chroma_client = ChromaClient(collection_name)

    def retrieve(self, query: str, top_k: int = 15):
        """
        Retrieves the top_k most relevant log entries from the vector database.
        """
        query_embedding = self.embedding_model.encode(query, convert_to_tensor=False)
        results = self.chroma_client.query_logs(query_embedding.tolist(), top_k)
        return results
