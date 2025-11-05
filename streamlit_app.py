from __future__ import annotations

import os
import pandas as pd
import streamlit as st

from llm import ChartCodeGenerator
from constants import (
    CHART_GEN,
    ENTRY,
    IMPROVEMENT_QUERY,
    ORIGINAL_QUERY,
)
from ui_components import (
    render_chart,
    render_improvement_form,
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

    if CHART_GEN not in st.session_state:
        st.session_state[CHART_GEN] = initial_chart_gen
    if ORIGINAL_QUERY not in st.session_state:
        st.session_state[ORIGINAL_QUERY] = ""
    if IMPROVEMENT_QUERY not in st.session_state:
        st.session_state[IMPROVEMENT_QUERY] = ""

    # Kick start the app by collecting a query
    if not st.session_state[ORIGINAL_QUERY]:
        def update_query():
            st.session_state[ORIGINAL_QUERY] = st.session_state['query_value']

        st.text_input("Enter your query", key='query_value')
        st.button("Submit", width='stretch', on_click=update_query)
        return

    # Show original query at top
    (f"Original query: {st.session_state[ORIGINAL_QUERY]}")

    # Control variables
    chart_gen = st.session_state[CHART_GEN]
    history_count = len(chart_gen.history)
    latest_entry = chart_gen.history[-1] if history_count > 0 else None
    current_entry = None
    improvement_query = st.session_state[IMPROVEMENT_QUERY]

    if history_count == 0:
        # Generate a chart to kick-start the session
        success, result = chart_gen.generate_chart_code(st.session_state[ORIGINAL_QUERY])
        if success:
            current_entry = result
        else:
            st.error(result['error'])
            current_entry = latest_entry
    elif history_count == 1 and not improvement_query:
        current_entry = latest_entry
    elif improvement_query and improvement_query != latest_entry['query']:
        success, result = chart_gen.improve_chart_code(improvement_query)
        if success:
            current_entry = result
        else:
            st.error(result['error'])
            current_entry = latest_entry
    else:
        current_entry = latest_entry

    if current_entry:
        col_l, col_r = st.columns([3, 1])
        with col_l:
            render_chart(current_entry, chart_gen.all_dfs)
        with col_r:
            render_improvement_form()
    
    if current_entry is not None:
        st.code(current_entry['code'])
    st.write(chart_gen.history)

if __name__ == "__main__":
    render_main()