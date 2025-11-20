import pandas as pd
from sentence_transformers import SentenceTransformer
from backend.repositories.vector_chroma_db.clean_data import clean_data
from backend.repositories.vector_chroma_db.chroma_client import ChromaClient


def run_and_seed_db():
    """This is a placeholder for the run_and_seed_db function."""
    columns_to_use = ['Timestamp', 'Downtime Minutes', 'Notes', 'Line']
    print("Reading CSV file...")
    try:
        df = pd.read_csv('data/downtime_logs.csv', usecols=columns_to_use)
    except FileNotFoundError:
        print("CSV file not found. Please ensure 'backend/data/downtime_logs.csv' exists.")
        return
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
        return

    print("Cleaning data...")
    cleaned_data = clean_data(df)

    print("Generating embeddings...")
    chroma_client = ChromaClient(collection_name="downtime_logs")
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
    cleaned_data['embeddings'] = cleaned_data['Notes'].apply(lambda x: embedding_model.encode(x).tolist())

    cleaned_data['Timestamp_unix'] = cleaned_data['Timestamp'].apply(
        lambda x: int(x.timestamp() if isinstance(x, pd.Timestamp) else int(x)))
    cleaned_data['Timestamp'] = cleaned_data['Timestamp'].astype(str)

    print("Seeding database...")
    documents = cleaned_data['Notes'].tolist()
    embeddings = cleaned_data['embeddings'].tolist()
    metadatas = cleaned_data[['Timestamp_unix', 'Downtime Minutes', 'Line', 'Timestamp']].to_dict(orient='records')

    chroma_client.add_embeddings_to_db(documents, embeddings, metadatas)
    print("Database seeding complete.")


if __name__ == "__main__":
    run_and_seed_db()
