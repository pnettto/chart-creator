import altair as alt
import numpy as np
import pandas as pd
import streamlit as st

from llm import generate_chart_code, generate_improved_chart

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
    if success:
        try:
            col1, col2 = st.columns([2, 1])
            with col1:
                exec(code_str, globals(), locals())
                
            with col2:
                st.header("Improve Chart")
                improvement = st.text_input("Describe your improvement", key="improvement_input")
                if st.button("Submit Improvement", key="improve_btn"):
                    if improvement:
                        st.session_state.query = st.session_state.query + " " + improvement
                        st.session_state.submitted = True
                        st.rerun()
        except Exception as e:
            st.write(f'There was an error, try again.')
            st.code(e)
        
        with st.expander("Show generated code", expanded=False):
            st.code(code_str)

        if st.button("Try again", key="try_again_btn", use_container_width=True):
            st.session_state.submitted = False
            st.rerun()

        st.button("Restart", on_click=restart, use_container_width=True)

    else:
        st.write('There was an error, try again. Code: 002.')