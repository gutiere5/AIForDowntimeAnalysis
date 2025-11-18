import chromadb
import uuid
from typing import List, Dict, Optional, Union
from chromadb import QueryResult


class ChromaClient:
    def __init__(self, collection_name: str = "log_embeddings", path: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self._get_or_create_collection(collection_name)

    def _get_or_create_collection(self, collection_name: str) -> chromadb.Collection:
        """
        Gets an existing ChromaDB collection or creates a new one if it doesn't exist.
        """
        try:
            collection = self.client.get_collection(name=collection_name)
            print(f"Collection '{collection_name}' already exists.")
        except: # chromadb.exceptions.CollectionNotFoundError:
            collection = self.client.create_collection(name=collection_name)
            print(f"Collection '{collection_name}' created.")
        return collection

    def add_log_embedding(self, log_entry: str, embedding: List[float], metadata: Optional[Dict] = None) -> None:
        """
        Adds a single log entry and its embedding to the ChromaDB collection.
        Generates a unique ID for each entry.
        """
        try:
            self.collection.add(
                documents=[log_entry],
                embeddings=[embedding],
                metadatas=[metadata if metadata else {"source": "log_processor"}],
                ids=[str(uuid.uuid4().hex)]
            )
            print(f"Successfully added log entry to collection '{self.collection.name}'.")
        except Exception as e:
            print(f"Error adding log embedding to ChromaDB: {e}")

    def add_embeddings_to_db(
        self,
        texts: List[str],
        embeddings: List[List[float]],
        metadatas: Optional[List[Dict]] = None,
        ids: Optional[List[str]] = None
    ) -> None:
        """
        Adds texts, embeddings, and optional metadata to a ChromaDB collection.
        If IDs are not provided, ChromaDB will generate them automatically.
        """
        if not ids:
            # Generate simple IDs if not provided
            ids = [f"doc{i}" for i in range(len(texts))]

        # Ensure metadatas list matches the length of texts if provided
        if metadatas and len(metadatas) != len(texts):
            raise ValueError("Length of metadatas must match length of texts.")

        try:
            self.collection.add(
                documents=texts,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            print(f"Successfully added {len(texts)} embeddings to collection '{self.collection.name}'.")
        except Exception as e:
            print(f"Error adding embeddings to ChromaDB: {e}")

    def query_logs(
        self,
        query_embeddings: List[List[float]],
        n_results: int = 5
    ) -> Union[QueryResult, dict[str, str]]:
        """
        Queries the ChromaDB collection with given embeddings and returns the top n_results.
        """
        try:
            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                include=['documents', 'distances', 'metadatas']
            )
            return results
        except Exception as e:
            print(f"Error querying ChromaDB: {e}")
            return {"error": str(e)}

# Example Usage
if __name__ == "__main__":
    from backend.repositories.vector_chroma_db.log_processor import log_to_text, generate_embedding

    # Initialize ChromaClient
    chroma_client = ChromaClient(collection_name="downtime_logs")

    # Prepare some example log entries
    example_logs = [
        {'id': 1, 'timestamp': '2025-09-22 09:15:00', 'machine_id': 'M3', 'reason_code': 'SENSOR_FAIL', 'duration_minutes': 25},
        {'id': 2, 'timestamp': '2025-09-22 14:30:00', 'machine_id': 'M1', 'reason_code': 'MATERIAL_JAM', 'duration_minutes': 40},
        {'id': 3, 'timestamp': '2025-09-23 11:05:00', 'machine_id': 'M2', 'reason_code': 'LUBE_LOW', 'duration_minutes': 35},
        {'id': 4, 'timestamp': '2025-09-23 15:10:00', 'machine_id': 'M2', 'reason_code': 'OVERHEAT', 'duration_minutes': 55},
    ]

    # Process logs and add to the database
    for log in example_logs:
        text = log_to_text(log)
        embedding = generate_embedding(text)
        if embedding:
            chroma_client.add_log_embedding(text, embedding, metadata=log)

    # Query the database
    query_text = "What caused machine M3 to stop?"
    query_embedding = generate_embedding(query_text)

    if query_embedding:
        print(f"\nQuerying for: '{query_text}'")
        results = chroma_client.query_logs([query_embedding], n_results=3)
        print("Query Results:")
        for i in range(len(results['documents'][0])):
            print(f"  Document: {results['documents'][0][i]}")
            print(f"  Distance: {results['distances'][0][i]}")
            print(f"  Metadata: {results['metadatas'][0][i]}")
            print("---------------------")
    else:
        print("Could not generate embedding for query.")
