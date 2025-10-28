import os
import time
import sys
import json
from chromadb import PersistentClient
from sentence_transformers import SentenceTransformer
import requests
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
QA_ENGINE = "openai"  # openai or ollama

def answer_with_openai(prompt):
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

def answer_with_ollama(prompt):
    OLLAMA_URL = "http://localhost:11434/api/generate"
    OLLAMA_MODEL = "deepseek-v3.1:671b-cloud" # deepseek-v3.1:671b-cloud or llama3.2

    payload = {
        "model": OLLAMA_MODEL,
        "prompt": prompt
    }
    response = requests.post(OLLAMA_URL, json=payload, stream=True)
    if response.status_code == 200:
        full_response = ""
        try:
            for line in response.iter_lines():
                if line:
                    try:
                        data = json.loads(line.decode('utf-8'))
                        full_response += data.get("response", "")
                    except Exception:
                        pass
            return full_response.strip()
        except Exception as e:
            return f"Error parsing Ollama response: {e}"
    else:
        return f"Ollama API error: {response.status_code}\n{response.text}"

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
    answer = ""

    print(prompt)
    exit()

    if QA_ENGINE == "openai":
        answer = answer_with_openai(prompt)
    elif QA_ENGINE == "ollama":
        answer = answer_with_ollama(prompt)
    else:
        print(f"Unknown QA_ENGINE '{QA_ENGINE}'. Please set QA_ENGINE to 'openai' or 'ollama'.")
    
    print(answer)
    end_time = time.time()
    print(f"\nTime taken: {end_time - start_time:.2f} seconds")