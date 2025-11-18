from backend.agents.llm_models.embedding_model import EMBEDDING_MODEL

def log_to_text(log_entry: dict) -> str:
    """
    Converts a single downtime log entry dictionary into a human-readable string.
    """
    timestamp = log_entry.get('timestamp', 'N/A')
    machine_id = log_entry.get('machine_id', 'N/A')
    reason_code = log_entry.get('reason_code', 'UNKNOWN_REASON')
    duration = log_entry.get('duration_minutes', 0)

    return (f"On {timestamp}, machine {machine_id} experienced a downtime event. "
            f"The reason identified was '{reason_code}', and it lasted for {duration} minutes.")

def generate_embedding(text: str) -> list[float]:
    """
    Generates a vector embedding for the given text using a preloaded SentenceTransformer model.
    """
    try:
        # The encode method returns a numpy array, convert to list for type consistency
        generated_embedding = EMBEDDING_MODEL.encode(text).tolist()
        return generated_embedding
    except Exception as ex:
        print(f"Error generating embedding: {ex}")
        return []

# Example usage (for testing purposes)
if __name__ == "__main__":
    example_log = {
        'id': 1,
        'timestamp': '2025-09-22 09:15:00',
        'machine_id': 'M3',
        'reason_code': 'SENSOR_FAIL',
        'duration_minutes': 25
    }
    text_representation = log_to_text(example_log)
    print(f"Text representation: {text_representation}")

    try:
        embedding = generate_embedding(text_representation)
        print(f"Embedding generated (first 5 elements): {embedding[:5]}...")
        print(f"Embedding dimension: {len(embedding)}")
    except Exception as e:
        print(f"Could not generate embedding: {e}")


