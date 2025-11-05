def PROMPT_RELEVANT_DFS(user_query, dfs_formatted):
    return (
        "You are given several sampled DataFrames from CSV files (random rows, to help understand the content as a whole). "
        "Your task is to determine which DataFrames are needed to answer the user's question. "
        "If the answer requires any calculation, lookup, or comparison, include all DataFrames that may contain relevant values, even if the question only mentions one. "
        "Pay special attention to columns that may be related (such as price, amount, salary, id, etc.), and include DataFrames that could be joined or referenced together. "
        "If there is any possibility that a DataFrame could be useful for answering the question, include it. "
        "Err on the side of including more DataFrames rather than missing one. "
        "Respond ONLY with a list of DataFrame names (filenames) that are relevant "
        "Do not use markdown code block. The format should be Python code that can be used with exec(), like this: ['df_x', 'df_y']\n\n"
        "Important: This prompt is supposed to aid on the creation of charts. If the user question does not specifically ask for something that could be used to generate a chart, respond simply: error\n\n"
        f"User question: {user_query}\n\n"
        f"Sampled DataFrames:\n{dfs_formatted}\n\n"
    )

def PROMPT_PYTHON_CODE(user_query, dfs_formatted):
    return (
        "Given several sampled DataFrames from CSV files, your task is to generate ONLY the Python code to create a Streamlit chart that answers the user's question. "
        "Each DataFrame is loaded as dfs['dataframe_name'], so never use the dataframe name directly, always use it as a key of the dfs dict."
        "pandas (pd), numpy (np), Streamlit (st), Altair (alt) and prophet (prophet) are available. DO NOT add imports for them or anything else. "
        "You must always create charts using st.altair_chart. Any kind of Altair chart (bar, line, scatter, etc.) may be used as appropriate. "
        "Return only executable Python code—no explanations, comments, or markdown code blocks. "
        "Do NOT use markdown code syntax (such as triple backticks or ```python) in your response. "
        "Comment each line to explain your reasoning for the changes made but keep it very short. "
        "If a chart cannot be created from the provided DataFrames, respond with and error explainig why not.\n\n"
        f"User question: {user_query}\n\n"
        f"Sampled DataFrames:\n{dfs_formatted}\n\n"
    )

def PROMPT_IMPROVE_CODE(user_query, code_generated, dfs_formatted, improvement_query):
    prompt = (
        "You are given Python code that generates a Streamlit chart. "
        "The user wants to improve the chart in a specific way. "
        "Your task is to generate ONLY the improved Python code for the chart, implementing the user's requested improvement as clearly and directly as possible. "
        "Preserve all existing chart functionality unless the improvement request requires a change. "
        "Comment each line to explain your reasoning for the changes made. "
        "pandas (pd), numpy (np), Streamlit (st), Altair (alt) and prophet (prophet) are available. DO NOT add imports for them or anything else. "
        "You must always create charts using st.altair_chart. Any kind of Altair chart (bar, line, scatter, etc.) may be used as appropriate. "
        "Do not add import statements. Return only executable Python code—no explanations, comments, or markdown code blocks. "
        "Return only executable Python code—no explanations, comments, or markdown code blocks. "
        "Do NOT use markdown code syntax (such as triple backticks or ```python) in your response. "
        "Make very short comments at all lines to explain your reasoning in creating them, but never create a comment block at the start.    "
        "If a chart cannot be created from the provided DataFrames, respond with and error explainig why not."
        "Important: you are supposed to aid on the improvement of charts. If the user question does not specifically ask for something that could be used to improve a chart or otherwise visualize data, respond simply: error\n\n"
        f"Original user query and past improvement queries (separated by /): {user_query}\n\n"
        f"Latest generated code:\n{code_generated}\n\n"
        f"Sampled DataFrames:\n{dfs_formatted}\n\n"
        f"User improvement request: {improvement_query}\n\n"
    )
    return prompt

def PROMPT_IDEAS(dfs_formatted):
    return (
        "List 10 prompts I could give an AI to explore the data in the sampled Dataframes, by creating a kind of chart. "
        "The prompt must be about chart creation. "
        "Make the prompt approachable and understandable for humans, though it's meant to an LLM. "
        "Add a component of interest or fun. "
        "It's ok to join dataframes if that would contribute to a more interesting exploraton. "
        "Answer in markdown format (only the bullet point list) and keep the prompts rather short (one sentence). \n\n"
        "The output format must be a markdowb bullet point list like this:"
        "Prompt 1: .... \n"
        "Prompt 2: .... \n"
        "Etc \n\n"
        f"Sampled DataFrames:\n{dfs_formatted}\n\n"
    )