import logging
import os
import ast
from openai import OpenAI
from dotenv import load_dotenv
from prompts import PROMPT_RELEVANT_DFS, PROMPT_PYTHON_CODE, PROMPT_IMPROVE_CODE

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY", "")
if not openai_api_key:
    print("Warning: OPENAI_API_KEY not set in .env file.")
openai_client = OpenAI(api_key=openai_api_key)
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def format_dfs_for_prompt(dfs):
    formatted = []
    for name, df in dfs.items():
        sample_size = min(5, len(df))
        formatted.append(f"DataFrame: {name}\n{df.sample(sample_size).to_csv(index=False, header=True, lineterminator='; ')}\n")
    return "\n".join(formatted)

def compose_prompt(prompt_func, *args):
    prompt = prompt_func(*args)
    return prompt
    
def ask_llm(prompt):
    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()


class ChartCodeGenerator:
    def __init__(self, all_dfs=[]):
        self.all_dfs = all_dfs
        self.history = []
        self.relevant_dfs_formatted = None

    def generate_chart_code(self, user_query: str):
        all_dfs_formatted_for_prompt = format_dfs_for_prompt(self.all_dfs)
        prompt = compose_prompt(PROMPT_RELEVANT_DFS, user_query, all_dfs_formatted_for_prompt)
        relevant_dfs_str = ask_llm(prompt)
        # relevant_dfs_str = "['monthly_spending_dataset_2020_2025']"

        if relevant_dfs_str == 'error':
            result = {
                'error': 'The query must be about chart creation'
            }
            return False, result

        try:
            relevant_dfs_names = ast.literal_eval(relevant_dfs_str)
        except Exception as e:
            result = {
                'error': f'Malformed dfs: {e}'
            }
            return False, result

        try:
            relevant_dfs = {df_name: self.all_dfs[df_name] for df_name in relevant_dfs_names}
        except KeyError as e:
            result = {
                'error': f'DataFrame not found: {e}'
            }
            return False, result

        self.relevant_dfs_formatted = format_dfs_for_prompt(relevant_dfs)
        prompt = compose_prompt(PROMPT_PYTHON_CODE, user_query, self.relevant_dfs_formatted)
        print(prompt)

        generated_code = ask_llm(prompt)
#         generated_code = """
# st.altair_chart(
#     alt.Chart(dfs['monthly_spending_dataset_2020_2025']).transform_fold(
#         # Fold the data to get each component in a single column for easier calculation
#         ["Groceries ($)", "Rent ($)", "Transportation ($)", "Gym ($)", "Utilities ($)",
#          "Healthcare ($)", "Investments ($)", "Savings ($)", "EMI/Loans ($)",
#          "Dining & Entertainment ($)", "Shopping & Wants ($)"],
#         as_=['Component', 'Amount']
#     ).transform_calculate(
#         # Calculate the percentage of each component relative to the income
#         Percentage='datum.Amount / datum["Income ($)"] * 100'
#     ).mark_bar().encode(
#         # X-axis: Month
#         x='yearmonth(Month):O',
#         # Y-axis: Percentage of income
#         y='sum(Percentage):Q',
#         # Color by spending component
#         color='Component:N',
#         # Tooltip to show details on hover
#         tooltip=['Component:N', 'sum(Amount):Q', 'sum(Percentage):Q']
#     ).properties(
#         # Set chart title
#         title='Percentage of Each Component of Monthly Spending Relative to Income'
#     ),
#     # Define the display settings for the chart
#     width='stretch'
# )
# """
        # Make sure to strip any code block markings, just in case it happens
        generated_code = "\n".join(
            line for line in generated_code.splitlines() if not line.strip().startswith("```")
        )

        history_entry = {
            'query': user_query,
            'code': generated_code
        }
        self.history.append(history_entry)
        
        return True, history_entry

    def improve_chart_code(self, improvement_query: str):
        if len(self.history) == 0:
            result = {
                'error': 'No chart code to improve. Generate a chart first.'
            }
            return False, result
        
        latest_entry = self.history[- 1]
        prompt = compose_prompt(
            PROMPT_IMPROVE_CODE,
            ' / '.join([entry['query'] for entry in self.history]),
            latest_entry['code'],
            self.relevant_dfs_formatted,
            improvement_query
        )
        print('IMPROVEMENT PROMPT', prompt)
        # prompt = compose_prompt(
        #     PROMPT_IMPROVE_CODE,
        #     improvement_query,
        #     latest_entry,
        #     self.relevant_dfs_formatted,
        # )

        improved_code_str = ask_llm(prompt)
#         improved_code_str = """
# st.altair_chart(
#     alt.Chart(dfs['monthly_spending_dataset_2020_2025']).transform_fold(
#         ["Groceries ($)", "Rent ($)", "Transportation ($)", "Gym ($)", "Utilities ($)",
#          "Healthcare ($)", "Investments ($)", "Savings ($)", "EMI/Loans ($)",
#          "Dining & Entertainment ($)", "Shopping & Wants ($)"],
#         as_=['Component', 'Amount']
#     ).transform_calculate(
#         Percentage='datum.Amount / datum["Income ($)"] * 100'
#     ).mark_bar(size=15, cornerRadiusTopLeft=4, cornerRadiusTopRight=4).encode(
#         x=alt.X('yearmonth(Month):O', title='Month', axis=alt.Axis(labelAngle=0)),
#         y=alt.Y('sum(Percentage):Q', title='% of Monthly Income'),
#         color=alt.Color('Component:N', title='Spending Category',
#                         scale=alt.Scale(scheme='tableau10')),
#         tooltip=[
#             alt.Tooltip('Component:N', title='Category'),
#             alt.Tooltip('sum(Amount):Q', title='Total ($)', format=','),
#             alt.Tooltip('sum(Percentage):Q', title='% of Income', format='.1f')
#         ]
#     ).properties(
#         title='Monthly Spending Breakdown as % of Income',
#         height=400
#     ).configure_title(
#         fontSize=18, fontWeight='bold', anchor='start'
#     ).configure_axis(
#         labelFontSize=12, titleFontSize=13
#     ).configure_legend(
#         titleFontSize=13, labelFontSize=11, orient='bottom'
#     ),
#     width='stretch'
# )
# """
        improved_code_str = "\n".join(
            line for line in improved_code_str.splitlines() if not line.strip().startswith("```")
        )

        if improved_code_str == 'error':
            result = {
                'error': 'The query must be about chart creation'
            }
            return False, result
        
        history_entry = {
            'query': improvement_query,
            'code': improved_code_str,
        }
        self.history.append(history_entry)
        return True, history_entry

    def get_history(self):
        return self.history