import altair as alt
import numpy as np
import pandas as pd
import prophet
import streamlit as st

from llm import ChartCodeGenerator


st.set_page_config(page_title="Natural Chart Creator", layout="wide")
st.title("Natural Chart Creator")

def handle_query_input():
    query = st.text_input("Enter your query", key="query_input")
    if st.button("Submit", use_container_width=True) or (query and st.session_state.query_input):
        st.session_state.submitted = True
        st.session_state.query = query or st.session_state.query_input

def execute_and_display_chart(code_str):
    col1, col2 = st.columns([2, 1])
    with col1:
        try:
            exec(code_str, globals(), locals())
        except Exception as e:
            st.write(f'There was an error')
            st.code(e)
            try_again_btn('exception')
    return col2

def improvement_form(chart_gen):
    with st.form("improvement_form"):
        improvement_text = st.text_area("Ask for an improvement", key="improvement_text")
        submitted = st.form_submit_button("Submit")
        if submitted and improvement_text:
            improve_success, improved_code = chart_gen.improve_chart_code(improvement_text)
            if improve_success:
                st.session_state.show_improved = True
                st.session_state.improvement_text_value = improvement_text
                st.rerun()
            else:
                st.write('Improvement failed:')
                st.code(improved_code)

def try_again_btn(btn_id):
    if st.button("Try again", key=f"try_again_btn_{btn_id}", use_container_width=True):
        st.session_state.show_improved = False
        st.rerun()

def restart_btn():
    if st.button("Restart", key="restart_btn", use_container_width=True):
        st.session_state.submitted = False
        st.session_state.query = ""
        st.session_state.improvement_text_value = ""
        st.session_state.show_improved = False

def show_code_expander(code_str):
    with st.expander("Show generated code", expanded=False):
        st.code(code_str)

def show_history(chart_gen):
    with st.expander("Show improvement history", expanded=False):
        for i, entry in enumerate(chart_gen.get_history()):
            if i > 0:
                st.markdown(f"---")
            if entry['improvement_query']:
                st.markdown(f"Improvement: {entry['improvement_query']}")
            else:
                st.markdown(f"Original query: {st.session_state.query}")
            with st.expander("Show generated code", expanded=False):
                st.code(entry['improved_code'] if entry['improved_code'] else entry['code'])
            if st.button(f"Recover", key=f"recover_{i}"):
                chart_gen.current_code = entry['improved_code'] if entry['improved_code'] else entry['code']
                st.session_state.show_improved = True
                st.session_state.improvement_text_value = entry.get('improvement_query', '')
                st.rerun()

if "chart_gen" not in st.session_state:
    st.session_state.chart_gen = ChartCodeGenerator()
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "query" not in st.session_state:
    st.session_state.query = ""

if not st.session_state.submitted:
    handle_query_input()
else:
    st.write(f"Query: **{st.session_state.query}**")
    chart_gen = st.session_state.chart_gen

    if not st.session_state.get("show_improved", False):
        success, response_str, dfs = chart_gen.generate_chart_code(st.session_state.query)
        st.session_state.last_code = response_str if success else None
        st.session_state.last_dfs = dfs if success else None
    else:
        success = True
        response_str = chart_gen.current_code
        dfs = chart_gen.dfs

    if success:
        code_str = response_str
        col2 = execute_and_display_chart(code_str)
        with col2:
            improvement_form(chart_gen)
            try_again_btn('default')
            restart_btn()
        show_code_expander(code_str)
        show_history(chart_gen)
    else:
        st.write('There was an error, try again. Code: 002.')
        st.code(response_str)