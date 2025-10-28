import os
import pandas as pd
from chromadb import PersistentClient
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Settings
CSV_FOLDER = os.path.abspath("./files")
CHROMA_DB_DIR = os.path.abspath("./chroma_db")
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # Use a fast, local model

# Initialize Chroma client
client = PersistentClient(path=CHROMA_DB_DIR)
collection = client.get_or_create_collection(name="data_collection")

# Load embedding model
embedder = SentenceTransformer(EMBEDDING_MODEL)

def chunk_text(text, chunk_size=200):
    # Simple chunking by character count
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

def index_csv_files():
    print(f"Indexing CSV files in: {CSV_FOLDER}")
    file_count = 0
    row_count = 0
    chunk_count = 0
    for filename in os.listdir(CSV_FOLDER):
        if filename.endswith(".csv"):
            file_count += 1
            filepath = os.path.join(CSV_FOLDER, filename)
            print(f"Processing file: {filename}")
            df = pd.read_csv(filepath)
            for idx, row in df.iterrows():
                row_count += 1
                row_text = ", ".join([f"{col}: {row[col]}" for col in df.columns])
                # Add all column names and values as metadata
                row_metadata = {col: row[col] for col in df.columns}
                metadata = {"source_file": filename, "row_index": idx, **row_metadata}
                chunks = chunk_text(row_text)
                for chunk in chunks:
                    chunk_count += 1
                    embedding = embedder.encode(chunk)
                    collection.add(
                        embeddings=[embedding],
                        documents=[chunk],
                        metadatas=[metadata],
                        ids=[f"{filename}_{idx}_{hash(chunk)}"]
                    )
    print(f"Indexed {file_count} files, {row_count} rows, {chunk_count} chunks.")
    print("Verifying collection contents...")
    print(f"Collection count: {collection.count()}")
    if collection.count() > 0:
        sample = collection.get(limit=3)
        print("Sample documents:")
        for doc, meta in zip(sample['documents'], sample['metadatas']):
            print(f"Doc: {doc}, Meta: {meta}")
    else:
        print("No documents found in collection.")

if __name__ == "__main__":
    index_csv_files()
