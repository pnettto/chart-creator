def prompt_relevant_dfs(user_query, dfs_formatted):
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

def prompt_python_code(user_query, dfs_formatted):
    return (
        "You are given several sampled DataFrames from CSV files (random rows, to help understand the content as a whole). "
        "Your task is to examine the user question and the sampled DataFrames, and return ONLY the Python code that will transform the relevant data into a Streamlit chart according to the user query request. "
        "Assume that each DataFrame is already loaded and assigned to a variable named dfs['dataframe_name']. "
        "Also assume that pandas (pd) and numpy (np) are available so no need to import them. "
        "The code will be executed in a Streamlit environment, so you can use Streamlit functions (such as st.line_chart, st.bar_chart, st.pyplot, etc.) to output the chart directly. "
        "Do not include any explanations, comments, or markdown code blocks—return only the Python code required to generate the chart. \n\n"
        "Do not use markdown code block. The format should be Python code that could be used with exec(). Only the code that will be executed, not the actual exec() call.\n\n"
        "If the user question cannot be answered with a chart using the provided DataFrames, respond with: error\n\n"
        f"User question: {user_query}\n\n"
        f"Sampled DataFrames:\n{dfs_formatted}\n\n"
    )
