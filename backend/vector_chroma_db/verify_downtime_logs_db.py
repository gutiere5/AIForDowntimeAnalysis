import json
from backend.vector_chroma_db.chroma_client import ChromaClient

def verify_db_contents():
    """
    Connects to the ChromaDB and prints its contents to verify seeding.
    """
    print("Connecting to ChromaDB...")
    try:
        chroma_client = ChromaClient(collection_name="log_embeddings", path="../chroma_db")
        collection = chroma_client.collection
        
        print(f"Successfully connected to collection: '{collection.name}'")
        
        # Retrieve all items from the collection
        # We ask for documents and metadatas, which are the most human-readable parts.
        results = collection.get(include=["metadatas", "documents"])
        
        count = len(results.get("ids", []))
        print(f"Found {count} entries in the database.")
        
        if count > 0:
            print("\n--- Database Contents ---")
            # Using zip to iterate through documents and metadatas together
            for doc, meta in zip(results.get("documents", []), results.get("metadatas", [])):
                print(f"\nDocument: {doc}")
                # Pretty-print the metadata dictionary
                print(f"Metadata: {json.dumps(meta, indent=2)}")
                print("---------------------")
        
    except Exception as e:
        print(f"An error occurred while trying to verify the database: {e}")

if __name__ == "__main__":
    verify_db_contents()
