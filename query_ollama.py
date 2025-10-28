import os
import time
import sys
import json
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY", "")
if not openai_api_key:
    print("Warning: OPENAI_API_KEY not set in .env file.")
openai_client = OpenAI(api_key=openai_api_key)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Settings
CHROMA_DB_DIR = "./database/chroma_db"
COLLECTION_NAME = "data_collection"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def answer_with_openai(prompt):
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    start_time = time.time()
    
    user_query = sys.argv[1]
    embedder = SentenceTransformer(EMBEDDING_MODEL)
    persistent_client = PersistentClient(path=CHROMA_DB_DIR)
    collection = persistent_client.get_collection(COLLECTION_NAME)
    query_embedding = embedder.encode(user_query)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=120
    )
    retrieved_docs = results['documents'][0]
    retrieved_metas = results['metadatas'][0]
    context = "\n".join(
        f"{doc} | metadata: {json.dumps(meta, ensure_ascii=False)}"
        for doc, meta in zip(retrieved_docs, retrieved_metas)
    )
    prompt = f"Use the following context to answer the question.\nContext:\n{context}\n\nQuestion: {user_query}\nAnswer:"
    answer = answer_with_openai(prompt)
    
    print(answer)
    end_time = time.time()
    print(f"\nTime taken: {end_time - start_time:.2f} seconds")