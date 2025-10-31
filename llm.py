
import os
import ast
import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv
from prompts import prompt_relevant_dfs, prompt_python_code, prompt_improve_code

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY", "")
if not openai_api_key:
    print("Warning: OPENAI_API_KEY not set in .env file.")
openai_client = OpenAI(api_key=openai_api_key)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

CSV_FOLDER = "./files"

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
        formatted.append(f"DataFrame: {name}\n{df.sample(sample_size).to_csv(index=False, header=True, lineterminator='; ')}\n")
    return "\n".join(formatted)

def ask_llm(prompt_func, *args):
    prompt = prompt_func(*args)
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


class ChartCodeGenerator:
    def __init__(self, csv_folder=CSV_FOLDER):
        self.csv_folder = csv_folder
        self.dfs = load_and_sample_csvs(self.csv_folder)
        self.current_query = None
        self.current_code = None
        self.current_relevant_dfs = None
        self.current_selected_dfs = None
        self.history = []  # Each entry: dict with keys: query, code, improvement_query, improved_code

    def generate_chart_code(self, user_query: str):
        self.current_query = user_query
        dfs_formatted = format_dfs_for_prompt(self.dfs)
        relevant_dfs_str = ask_llm(prompt_relevant_dfs, user_query, dfs_formatted)

        if relevant_dfs_str == 'error':
            return False, 'The query must be about chart creation'

        try:
            relevant_dfs = ast.literal_eval(relevant_dfs_str)
        except Exception as e:
            return False, f'LLM malfunction: {e}'

        self.current_relevant_dfs = relevant_dfs
        try:
            selected_dfs = {df_key: self.dfs[df_key] for df_key in relevant_dfs}
        except KeyError as e:
            return False, f'DataFrame not found: {e}'

        self.current_selected_dfs = selected_dfs
        selected_dfs_formatted = format_dfs_for_prompt(selected_dfs)
        python_code_str = ask_llm(prompt_python_code, user_query, selected_dfs_formatted)
        python_code_str = "\n".join(
            line for line in python_code_str.splitlines() if not line.strip().startswith("```")
        )

        self.current_code = python_code_str
        self.history.append({
            'query': user_query,
            'code': python_code_str,
            'relevant_dfs': relevant_dfs,
            'selected_dfs': list(selected_dfs.keys()),
            'improvement_query': None,
            'improved_code': None
        })
        return True, python_code_str, self.dfs

    def improve_chart_code(self, improvement_query: str):
        if self.current_code is None or self.current_query is None or self.current_selected_dfs is None:
            return False, 'No chart code to improve. Generate a chart first.'

        selected_dfs_formatted = format_dfs_for_prompt(self.current_selected_dfs)
        improved_code_str = ask_llm(
            prompt_improve_code,
            self.current_query,
            selected_dfs_formatted,
            self.current_code,
            improvement_query
        )
        improved_code_str = "\n".join(
            line for line in improved_code_str.splitlines() if not line.strip().startswith("```")
        )
        self.history.append({
            'query': self.current_query,
            'code': self.current_code,
            'relevant_dfs': self.current_relevant_dfs,
            'selected_dfs': list(self.current_selected_dfs.keys()),
            'improvement_query': improvement_query,
            'improved_code': improved_code_str
        })
        self.current_code = improved_code_str
        return True, improved_code_str

    def get_history(self):
        return self.history