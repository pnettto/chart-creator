from __future__ import annotations

import os
import pandas as pd
import streamlit as st

from llm import ChartCodeGenerator
from constants import (
    CHART_GEN,
    ENTRY_HISTORY_INDEX,
    IMPROVEMENT_ENTRY_INDEX,
    IMPROVEMENT_QUERY,
    ORIGINAL_QUERY,
)
from ui_components import (
    render_chart,
    render_history,
    render_improvement_form,
    render_version_navigation
)

def load_dfs():
    csv_folder = "./files"
    dfs = {}
    for filename in os.listdir(csv_folder):
        if filename.endswith(".csv"):
            filepath = os.path.join(csv_folder, filename)
            name, _ = os.path.splitext(filename)
            dfs[name] = pd.read_csv(filepath)
    return dfs

# Load all available dfs
all_dfs = load_dfs()

initial_chart_gen = ChartCodeGenerator(all_dfs=all_dfs)

def render_main() -> None:
    st.set_page_config(page_title="Natural Chart Creator", layout="wide")
    st.title("Natural Chart Creator")
    st.markdown("""
    <style>
    .stMainBlockContainer {
        padding: 3rem;
    }
    </style>
""", unsafe_allow_html=True)

    # Initialize session variables
    if CHART_GEN not in st.session_state:
        st.session_state[CHART_GEN] = initial_chart_gen
    if ENTRY_HISTORY_INDEX not in st.session_state:
        st.session_state[ENTRY_HISTORY_INDEX] = None
    if ORIGINAL_QUERY not in st.session_state:
        st.session_state[ORIGINAL_QUERY] = ""
    if IMPROVEMENT_ENTRY_INDEX not in st.session_state:
        st.session_state[IMPROVEMENT_ENTRY_INDEX] = None
    if IMPROVEMENT_QUERY not in st.session_state:
        st.session_state[IMPROVEMENT_QUERY] = ""

    # Start the app by collecting a query
    if not st.session_state[ORIGINAL_QUERY]:
        def execute_original_query():
            st.session_state[ORIGINAL_QUERY] = st.session_state['query_value']
            st.session_state['trigger_execute_original_query'] = True

        st.text_input("Enter your query", key='query_value')
        if st.button("Submit", width='stretch', key="query_button"):
            execute_original_query()

        if st.session_state.get('trigger_execute_original_query', False):
            st.session_state['trigger_execute_original_query'] = False
            st.rerun()

        return

    # Show original query at top
    (f"Original query: {st.session_state[ORIGINAL_QUERY]}")

    # Session variables
    chart_gen = st.session_state[CHART_GEN]
    entry_history_index = st.session_state[ENTRY_HISTORY_INDEX] # Selected from navigation and history
    improvement_entry_index = st.session_state[IMPROVEMENT_ENTRY_INDEX]
    improvement_query = st.session_state[IMPROVEMENT_QUERY]
    
    # Other control variables
    history_count = len(chart_gen.history)
    latest_entry = chart_gen.history[-1] if history_count > 0 else None
    current_entry = None
    current_entry_index = None

    if history_count == 0: # Start the chart engine
        success, result = chart_gen.generate_chart_code(st.session_state[ORIGINAL_QUERY])
        if success:
            current_entry = result
            current_entry_index = 0
        else:
            st.error(result['error'])
            if st.button("Reload App", width='stretch'):
                st.session_state.clear()
                st.rerun()
    elif entry_history_index is not None: # An specific version has been selected
        current_entry = chart_gen.history[entry_history_index]
        current_entry_index = entry_history_index
    elif improvement_query and improvement_query != latest_entry['query']: # Improvement request was made (make sure improvement query is different from last entry's)
        success, result = chart_gen.improve_chart_code(improvement_query, improvement_entry_index)
        if success:
            current_entry = result
            current_entry_index = len(chart_gen.history) - 1
        else:
            st.error(result['error'])
            current_entry = latest_entry
            current_entry_index = len(chart_gen.history) - 1
    else:
        current_entry = latest_entry
        current_entry_index = len(chart_gen.history) - 1

    if current_entry:
        col_l, col_r = st.columns([3, 1])
        with col_l:
            render_chart(current_entry, chart_gen.all_dfs)
        with col_r:
            render_improvement_form(current_entry_index)
            render_version_navigation(chart_gen.history, current_entry_index)

    render_history(chart_gen.history, chart_gen.all_dfs)

if __name__ == "__main__":
    render_main()