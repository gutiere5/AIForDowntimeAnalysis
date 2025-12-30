import pandas as pd
from repositories.vector_chroma_db.clean_data import clean_data
from repositories.vector_chroma_db.chroma_client import ChromaClient


def run_and_seed_db():
    """This is a placeholder for the run_and_seed_db function."""
    columns_to_use = ['Timestamp', 'Downtime Minutes', 'Notes', 'Line']
    print("Reading CSV file...")
    try:
        csv_path = 'data/downtime_logs.csv'
        df = pd.read_csv(csv_path, usecols=columns_to_use)
    except FileNotFoundError:
        print(f"CSV file not found at {csv_path}. Please ensure 'backend/data/downtime_logs.csv' exists.")
        return
    except Exception as e:
        print(f"An error occurred while reading the CSV file: {e}")
        return

    print("Cleaning data...")
    cleaned_data = clean_data(df)

    print("Seeding database...")
    chroma_client = ChromaClient(collection_name="downtime_logs", path="./chroma_db")
    cleaned_data['Timestamp_unix'] = cleaned_data['Timestamp'].apply(
        lambda x: int(x.timestamp() if isinstance(x, pd.Timestamp) else int(x)))
    cleaned_data['Timestamp'] = cleaned_data['Timestamp'].astype(str)

    documents = cleaned_data['Notes'].tolist()
    metadatas = cleaned_data[['Timestamp_unix', 'Downtime Minutes', 'Line', 'Timestamp']].to_dict(orient='records')

    chroma_client.add_items(documents, metadatas)
    print("Database seeding complete.")


if __name__ == "__main__":
    run_and_seed_db()
