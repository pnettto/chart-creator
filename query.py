import os
import sys
import time
import ast
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY", "")
if not openai_api_key:
    print("Warning: OPENAI_API_KEY not set in .env file.")
openai_client = OpenAI(api_key=openai_api_key)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

CSV_FOLDER = "./database/files"

def load_and_sample_csvs(folder):
    dfs = {}
    for filename in os.listdir(folder):
        if filename.endswith(".csv"):
            filepath = os.path.join(folder, filename)
            name, _ = os.path.splitext(filename)
            dfs[name] = pd.read_csv(filepath)
    return dfs

def format_dfs_for_prompt(dfs):
    formatted = []
    for name, df in dfs.items():
        sample_size = min(5, len(df))
        # formatted.append(f"DataFrame: {name}\n{df.sample(sample_size).to_markdown(index=False)}\n")
        formatted.append(f"DataFrame: {name}\n{df.sample(sample_size).to_csv(index=False, header=True, lineterminator='; ')}\n")
    return "\n".join(formatted)

# Do not explain your answer, just output the list

def ask_openai_which_dfs(user_query, dfs_formatted):
    prompt = (
        "You are given several sampled DataFrames from CSV files (random rows, to help understand the content as a whole). "
        "Your task is to determine which DataFrames are needed to answer the user's question. "
        "If the answer requires any calculation, lookup, or comparison, include all DataFrames that may contain relevant values, even if the question only mentions one. "
        "Pay special attention to columns that may be related (such as price, amount, salary, id, etc.), and include DataFrames that could be joined or referenced together. "
        "If there is any possibility that a DataFrame could be useful for answering the question, include it. "
        "Err on the side of including more DataFrames rather than missing one. "
        "Respond ONLY with a list of DataFrame names (filenames) that are relevant "
        "Do not use markdown code block. The format should be Python code that can be used with exec(), like this: ['df_x', 'df_y']\n\n"
        f"User question: {user_query}\n\n"
        f"Sampled DataFrames:\n{dfs_formatted}\n\n"
        "Relevant DataFrames:"
    )
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    start_time = time.time()
    if len(sys.argv) < 2:
        print("Usage: python query_ollama.py <your question>")
        sys.exit(1)
    user_query = sys.argv[1]

    dfs = load_and_sample_csvs(CSV_FOLDER)
    dfs_formatted = format_dfs_for_prompt(dfs)
    relevant_dfs = ask_openai_which_dfs(user_query, dfs_formatted)
    print("LLM result: ", relevant_dfs)
    list_dfs = []
    try:
        list_dfs = ast.literal_eval(relevant_dfs)
        print("Exec result: ", list_dfs)
    except:
        print('Could not parse the returned dfs')
        exit()
    end_time = time.time()
    print(f"\nTime taken: {end_time - start_time:.2f} seconds")

    for df_key in list_dfs:
        print(f"Sample from {df_key}:\n{dfs[df_key].sample(1).to_string(index=False)}\n")