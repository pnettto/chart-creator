import streamlit as st
import numpy as np
import pandas as pd

from llm import generate_chart_code

st.set_page_config(page_title="Query Chart App", layout="wide")

st.title("Query Chart App")
# Use session state to manage flow
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "query" not in st.session_state:
    st.session_state.query = ""

def restart():
    st.session_state.submitted = False
    st.session_state.query = ""

if not st.session_state.submitted:
    query = st.text_input("Enter your query", key="query_input")
    if st.button("Submit", use_container_width=True) or (query and st.session_state.query_input):
        st.session_state.submitted = True
        st.session_state.query = query or st.session_state.query_input
else:
    st.write(f"Query: **{st.session_state.query}**")
    
    success, code_str, dfs = generate_chart_code(st.session_state.query)
    # Clean up code block markers if present
    code_str = code_str.strip().removeprefix("```python").removeprefix("```").removesuffix("```")

    if success and :
        print('Code: ',  code_str)
        try:
            exec(code_str, globals(), locals())
        except:
            st.write('There was an error, try again.')
    else:
        st.write('There was an error, try again.')

    st.button("Restart", on_click=restart, use_container_width=True)
