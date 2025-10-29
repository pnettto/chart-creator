import os
import ast
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from prompts import relevant_dfs_selection_prompt, relevant_dfs_python_code

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

def ask_openai_which_dfs(user_query, dfs_formatted):
    prompt = relevant_dfs_selection_prompt(user_query, dfs_formatted)
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def ask_openai_python_code(user_query, dfs_formatted):
    prompt = relevant_dfs_python_code(user_query, dfs_formatted)
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def generate_chart_code(user_query: str):
    dfs = load_and_sample_csvs(CSV_FOLDER)
    dfs_formatted = format_dfs_for_prompt(dfs)
    relevant_dfs_str = ask_openai_which_dfs(user_query, dfs_formatted)
    if relevant_dfs_str == 'error':
        return False, 'The query must be about chart creation'
    try:
        relevant_dfs = ast.literal_eval(relevant_dfs_str)
    except Exception as e:
        return False, f'LLM Step 1 malfunction: {e}'
    try:
        selected_dfs = {df_key: dfs[df_key] for df_key in relevant_dfs}
    except KeyError as e:
        return False, f'DataFrame not found: {e}'
    selected_dfs_formatted = format_dfs_for_prompt(selected_dfs)
    python_code_str = ask_openai_python_code(user_query, selected_dfs_formatted)
    return True, python_code_str, dfs