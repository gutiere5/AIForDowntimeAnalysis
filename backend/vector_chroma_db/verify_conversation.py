from backend.vector_chroma_db.chroma_client import ChromaClient

def verify_conversation(conversation_id: str):
    """
    Connects to the CheromaDB and retrieves the spcified conversation.
    """
    print(f"Attempting to retrieve conversation with ID: {conversation_id}")
    
    # 1. Initialize the ChromaClient for the 'conversations' collection
    conversation_client = ChromaClient(collection_name="conversations", path="../chroma_db")
    
    # 2. Retrieve the conversation data
    conversation_data = conversation_client.get_conversation(conversation_id)
    
    # 3. Print the results
    if conversation_data:
        print("\n--- Conversation Found! ---")
        print("\n[Metadata]:")
        for key, value in conversation_data['metadata'].items():
            print(f"  {key}: {value}")
        
        print("\n[Conversation History]:")
        print(conversation_data['history_text'])
        print("\n---------------------------")
    else:
        print("\n--- Conversation Not Found ---")
        print("Please check the following:")
        print("  - Is the backend server running?")
        print("  - Did you copy the correct conversation ID?")
        print("  - Has the conversation been fully completed in the frontend?")

if __name__ == "__main__":
    verify_conversation("23f60012-d351-4d32-98ea-2f9fbce7adb7")
