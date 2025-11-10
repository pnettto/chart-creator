from __future__ import annotations

import os
import pandas as pd
import streamlit as st

from llm import ChartCodeGenerator
from constants import (
    CHART_GEN,
    ENTRY_HISTORY_INDEX,
    LOCAL_STORAGE_HISTORY,
    IMPROVEMENT_ENTRY_INDEX,
    IMPROVEMENT_QUERY,
    ORIGINAL_QUERY,
)
from history import (
    render_chart_history,
    render_local_storage_history_recovering_tool_load,
    render_local_storage_recovering_tool_save,
    render_version_navigation,
    sync_local_storage_history_to_session,
)
from ui_components import (
    render_chart,
    render_improvement_form
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
    if LOCAL_STORAGE_HISTORY not in st.session_state or st.session_state[LOCAL_STORAGE_HISTORY] is None:
        sync_local_storage_history_to_session()

    chart_gen = st.session_state[CHART_GEN]
    entry_history_index = st.session_state[ENTRY_HISTORY_INDEX] # Selected from navigation and history
    improvement_entry_index = st.session_state[IMPROVEMENT_ENTRY_INDEX]
    improvement_query = st.session_state[IMPROVEMENT_QUERY]


    # Start the app by collecting a query
    if not st.session_state[ORIGINAL_QUERY]:
        col_l, col_r = st.columns([2, 1])
        with col_l:
            # Initial query form
            def execute_original_query():
                st.session_state[ORIGINAL_QUERY] = st.session_state['query_value']
                st.session_state['trigger_execute_original_query'] = True

            st.text_input("Enter your query", key='query_value')
            if st.button("Submit", width='stretch', key="query_btn"):
                execute_original_query()

            if st.session_state.get('trigger_execute_original_query', False):
                st.session_state['trigger_execute_original_query'] = False
                st.rerun()

        with col_r:
            # Move "Get prompt ideas" button further down the page
            st.markdown("<div style='height: 85px;'></div>", unsafe_allow_html=True)
            if st.button("Get prompt ideas", key="prompt_ideas_btn"):
                prompt_ideas = chart_gen.generate_prompt_ideas()
                if prompt_ideas:
                    st.markdown('### Prompt ideas')
                    st.markdown(prompt_ideas)
        
        st.markdown('---')
        render_local_storage_history_recovering_tool_load(chart_gen)
        return


    # Show original query at top
    (f"Original query: {st.session_state[ORIGINAL_QUERY]}")

    # Other control variables
    history_count = len(chart_gen.history)
    latest_entry = chart_gen.history[-1] if history_count > 0 else None
    current_entry = None
    current_entry_index = None


    case = None
    if history_count == 0:
        case = "start"
    elif entry_history_index is not None:
        case = "version_selected"
    elif improvement_query and improvement_query != (latest_entry['query'] if latest_entry else None):
        case = "improvement"
    else:
        case = "default"

    match case:
        case "start":
            success, result = chart_gen.generate_chart_code(st.session_state[ORIGINAL_QUERY])
            if success:
                current_entry = result
                current_entry_index = 0
            else:
                st.error(result['error'])
                if st.button("Reload App", width='stretch'):
                    st.session_state.clear()
                    st.rerun()
        case "version_selected":
            current_entry = chart_gen.history[entry_history_index]
            current_entry_index = entry_history_index
        case "improvement":
            success, result = chart_gen.improve_chart_code(improvement_query, improvement_entry_index)
            if success:
                current_entry = result
                current_entry_index = len(chart_gen.history) - 1
            else:
                st.error(result['error'])
                current_entry = latest_entry
                current_entry_index = len(chart_gen.history) - 1
        case "default":
            current_entry = latest_entry
            current_entry_index = len(chart_gen.history) - 1


    if current_entry:
        col_l, col_r = st.columns([3, 1])
        with col_l:
            # Current char to display
            render_chart(current_entry, chart_gen.all_dfs)
        with col_r:
            # Controls
            render_improvement_form(current_entry_index)
            render_version_navigation(chart_gen.history, current_entry_index)

    render_chart_history(chart_gen.history, chart_gen.all_dfs)

    st.markdown('---')

    col_l, col_c, col_r = st.columns([1, 2, 1])
    with col_l:
        st.markdown('### Save this exploration')
        render_local_storage_recovering_tool_save(chart_gen)
    with col_c:
        render_local_storage_history_recovering_tool_load(chart_gen)
    with col_r:
        st.markdown('### Restart')
        if st.button("Restart", key="restart_btn"):
            st.session_state.clear()
            st.rerun()

if __name__ == "__main__":
    render_main()