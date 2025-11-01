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
        st.session_state.code_generated = False

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
        st.session_state.code_generated = False

def show_code_expander(code_str):
    with st.expander("Show generated code", expanded=False):
        st.code(code_str)

def show_history(chart_gen):
    with st.expander("Show history", expanded=False):
        history = chart_gen.get_history()
        for i, entry in enumerate(history):
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
                st.session_state.history_index = i
                st.rerun()

def show_version_navigation(chart_gen):
    history = chart_gen.get_history()
    if "history_index" not in st.session_state:
        st.session_state.history_index = len(history) - 1
    col_prev, col_next = st.columns([1, 1])
    with col_prev:
        if st.button("Prev", key="prev_btn", use_container_width=True, disabled=st.session_state.history_index <= 0):
            st.session_state.history_index = max(0, st.session_state.history_index - 1)
            entry = history[st.session_state.history_index]
            chart_gen.current_code = entry['improved_code'] if entry['improved_code'] else entry['code']
            st.session_state.show_improved = True
            st.session_state.improvement_text_value = entry.get('improvement_query', '')
            st.rerun()
    with col_next:
        if st.button("Next", key="next_btn", use_container_width=True, disabled=st.session_state.history_index >= len(history) - 1):
            st.session_state.history_index = min(len(history) - 1, st.session_state.history_index + 1)
            entry = history[st.session_state.history_index]
            chart_gen.current_code = entry['improved_code'] if entry['improved_code'] else entry['code']
            st.session_state.show_improved = True
            st.session_state.improvement_text_value = entry.get('improvement_query', '')
            st.rerun()
    # Show info about current version
    entry = history[st.session_state.history_index]
    st.markdown(f"{st.session_state.history_index + 1}/{len(history)} - {entry['improvement_query'] if entry['improvement_query'] else st.session_state.query}")

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
        if not st.session_state.get("code_generated", False):
            success, response_str, dfs = chart_gen.generate_chart_code(st.session_state.query)
            st.session_state.last_code = response_str if success else None
            st.session_state.last_dfs = dfs if success else None
            st.session_state.code_generated = True
            # Reset history index to latest
            if "history_index" in st.session_state:
                del st.session_state["history_index"]
        else:
            success = st.session_state.last_code is not None
            response_str = st.session_state.last_code
            dfs = st.session_state.last_dfs
    else:
        success = True
        # Use selected version if navigating, else latest
        history = chart_gen.get_history()
        idx = st.session_state.get("history_index", len(history) - 1)
        entry = history[idx]
        response_str = entry['improved_code'] if entry['improved_code'] else entry['code']
        dfs = chart_gen.dfs

    if success:
        code_str = response_str
        col2 = execute_and_display_chart(code_str)
        with col2:
            improvement_form(chart_gen)
            show_version_navigation(chart_gen)
            btn_l, btn_r = st.columns(2)
            with btn_l:
                try_again_btn('default')
            with btn_r:
                restart_btn()
        show_history(chart_gen)
    else:
        st.write('There was an error, try again. Code: 002.')
        st.code(response_str)