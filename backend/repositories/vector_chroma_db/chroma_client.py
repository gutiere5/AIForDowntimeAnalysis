import chromadb
import uuid
from typing import List, Dict, Optional, Union
import logging
from chromadb.utils.embedding_functions.sentence_transformer_embedding_function import \
    SentenceTransformerEmbeddingFunction


class ChromaClient:
    def __init__(self, collection_name, path: str = "./chroma_db"):
        self.logger = logging.getLogger(__name__)
        self.client = chromadb.PersistentClient(path=path)
        self.embedding_function = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.collection = self._get_or_create_collection(collection_name)

    def _get_or_create_collection(self, collection_name: str) -> chromadb.Collection:
        try:
            collection = self.client.get_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            self.logger.info(f"Collection '{collection_name}' already exists.")
        except Exception:
            collection = self.client.create_collection(
                name=collection_name,
                embedding_function=self.embedding_function
            )
            self.logger.info(f"Collection '{collection_name}' created.")
        return collection

    def add_single_item(self, ids: Optional[str], document: str, metadata: Optional[Dict]) -> None:
        ids = str(uuid.uuid4().hex) if not ids else ids
        metadata = [metadata] if metadata else None

        try:
            self.collection.add(
                documents=[document],
                metadatas=metadata,
                ids=[ids]
            )
            self.logger.info(f"Successfully added log entry to collection '{self.collection.name}'.")
        except Exception as e:
            self.logger.info(f"Error adding log embedding to ChromaDB: {e}")

    def add_items(
            self,
            documents: List[str],
            metadatas: Optional[List[Dict]] = None,
            ids: Optional[List[str]] = None
    ) -> None:
        if not ids:
            ids = [str(uuid.uuid4().hex) for _ in range(len(documents))]

        if metadatas and len(metadatas) != len(documents):
            self.logger.warning("Length of metadatas does not match length of documents.")
            raise ValueError("Length of metadatas must match length of documents.")

        try:
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            self.logger.info(f"Successfully added {len(documents)} embeddings to collection '{self.collection.name}'.")
        except Exception as e:
            self.logger.error(f"Error adding embeddings to ChromaDB: {e}")

    def query_items(
            self,
            query_texts: Optional[List[str]] = None,
            where: Optional[Dict[str, Union[str, int, float]]] = None,
            n_results: int = 5
    ):
        self.logger.info(f"Querying ChromaDB for {query_texts} using {n_results} results in {self.collection.name} collection.")
        try:
            collection_results = self.collection.query(
                query_texts=query_texts,
                n_results=n_results,
                where=where,
                include=['documents', 'metadatas']
            )
            if collection_results and collection_results.get('documents'):
                self.logger.info(f"Successfully retrieved {len(collection_results['documents'])} documents from ChromaDB.")
                if len(collection_results['documents']) > 0 :
                    self.logger.info(f"Showing one result: Document: {collection_results['documents'][0]}, Metadata: {collection_results['metadatas'][0]}")
            else:
                self.logger.info("No documents found.")
            return collection_results
        except Exception as e:
            self.logger.info(f"Error querying ChromaDB: {e}")
            return {"error": str(e)}

    def get_items(
            self,
            where: Optional[Dict[str, Union[str, int, float]]] = None,
    ):
        try:
            collection_results = self.collection.get(
                where=where,
                include=['documents', 'metadatas', 'ids']
            )
            return collection_results
        except Exception as e:
            self.logger.info(f"Error retrieving logs from ChromaDB: {e}")
            return {"error": str(e)}

    def upsert_single_item(self, id: str, document: str, metadata: Optional[Dict] = None) -> None:
        try:
            metadata = [metadata] if metadata else None
            self.collection.upsert(
                ids=[id],
                documents=[document],
                metadatas=metadata
            )
            self.logger.info(f"Successfully upserted item with ID '{id}' to collection '{self.collection.name}'.")
        except Exception as e:
            self.logger.error(f"Error upserting item to ChromaDB: {e}")

    def delete_item(self, id: str) -> None:
        try:
            self.collection.delete(ids=[id])
            self.logger.info(f"Successfully deleted item with ID '{id}' from collection '{self.collection.name}'.")
        except Exception as e:
            self.logger.error(f"Error deleting item from ChromaDB: {e}")
