import chromadb
import uuid
from typing import List, Dict, Optional, Union
import logging


class ChromaClient:
    def __init__(self, collection_name: str = "log_embeddings", path: str = "./chroma_db"):
        self.logger = logging.getLogger(__name__)
        self.client = chromadb.PersistentClient(path=path)
        self.collection = self._get_or_create_collection(collection_name)

    def _get_or_create_collection(self, collection_name: str) -> chromadb.Collection:
        """
        Gets an existing ChromaDB collection or creates a new one if it doesn't exist.
        """
        try:
            collection = self.client.get_collection(name=collection_name)
            self.logger.info(f"Collection '{collection_name}' already exists.")
        except:  # chromadb.exceptions.CollectionNotFoundError:
            collection = self.client.create_collection(name=collection_name)
            self.logger.info(f"Collection '{collection_name}' created.")
        return collection

    def add_single_embedding(self, document: str, embedding: List[float], metadata: Optional[Dict] = None) -> None:
        """
        Adds a single log entry and its embedding to the ChromaDB collection.
        Generates a unique ID for each entry.
        """
        try:
            self.collection.add(
                documents=[document],
                embeddings=[embedding],
                metadatas=[metadata],
                ids=[str(uuid.uuid4().hex)]
            )
            self.logger.info(f"Successfully added log entry to collection '{self.collection.name}'.")
        except Exception as e:
            self.logger.info(f"Error adding log embedding to ChromaDB: {e}")

    def add_embeddings_to_db(
            self,
            documents: List[str],
            embeddings: List[List[float]],
            metadatas: Optional[List[Dict]] = None,
            ids: Optional[List[str]] = None
    ) -> None:
        """
        Adds texts, embeddings, and optional metadata to a ChromaDB collection.
        If IDs are not provided, ChromaDB will generate them automatically.
        """
        if not ids:
            ids = [str(uuid.uuid4().hex) for _ in range(len(documents))]

        if metadatas and len(metadatas) != len(documents):
            self.logger.warning("Length of metadatas does not match length of documents.")
            raise ValueError("Length of metadatas must match length of documents.")

        try:
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            self.logger.info(f"Successfully added {len(documents)} embeddings to collection '{self.collection.name}'.")
        except Exception as e:
            self.logger.error(f"Error adding embeddings to ChromaDB: {e}")

    def query_logs(
            self,
            query_embeddings: List[List[float]],
            where: Optional[Dict[str, Union[str, int, float]]] = None,
            n_results: int = 5
    ):
        try:
            collection_results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where,
                include=['documents', 'embeddings', 'metadatas']
            )
            return collection_results
        except Exception as e:
            self.logger.info(f"Error querying ChromaDB: {e}")
            return {"error": str(e)}

    def get_logs(
            self,
            where: Optional[Dict[str, Union[str, int, float]]] = None,
    ):
        try:
            collection_results = self.collection.get(
                where=where,
                include=['documents', 'embeddings', 'metadatas']
            )
            return collection_results
        except Exception as e:
            self.logger.info(f"Error retrieving logs from ChromaDB: {e}")
            return {"error": str(e)}
