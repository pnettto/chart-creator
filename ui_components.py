from __future__ import annotations

import altair as alt
import numpy as np
import pandas as pd
import prophet
import streamlit as st

from constants import (
    ENTRY_HISTORY_INDEX,
    IMPROVEMENT_ENTRY_INDEX,
    IMPROVEMENT_QUERY,
)

def render_chart(entry, dfs) -> None:
    try:
        # Restricted global context for exec
        _globals = {
            "alt": alt,
            "np": np,
            "pd": pd,
            "prophet": prophet,
            "st": st,
            "dfs": dfs,
        }
        exec(entry['code'], _globals, {})
    except Exception as e:
        st.write("There was an error. Navigate to the latest working version and submit a new improvement query.")
        with st.expander('Show code', expanded=False):
            st.code(entry['code'])
        with st.expander('Show error', expanded=False):
            st.code(e)
            def fix_error(e):
                st.session_state[IMPROVEMENT_QUERY] = f"Fix this error: \n {e}"
                st.session_state['trigger_fix_error'] = True

            if st.button("Fix", width='stretch'):
                fix_error(e)

            if st.session_state.get('trigger_fix_error', False):
                st.session_state['trigger_fix_error'] = False 
                st.rerun()


def render_improvement_form(improvement_entry_index) -> None:
    def request_improvement():
        st.session_state[IMPROVEMENT_QUERY] = st.session_state['current_improvement_query_value']
        st.session_state[IMPROVEMENT_ENTRY_INDEX] = improvement_entry_index
        st.session_state[ENTRY_HISTORY_INDEX] = None
        st.session_state['trigger_request_improvement'] = True

    st.text_area("Ask for an improvement", key='current_improvement_query_value', height=200)
    if st.button("Submit", width='stretch', key="current_improvement_query_btn"):
        request_improvement()

    if st.session_state.get('trigger_request_improvement', False):
        st.session_state['trigger_request_improvement'] = False 
        st.rerun()

def render_version_navigation(history, current_index) -> None:
    """Prev/Next navigation for code versions with current version info."""
    col_prev, col_next = st.columns([1, 1])
    with col_prev:
        if st.button("Prev", key="prev_btn", disabled=current_index is 0, width='stretch'):
            st.session_state[ENTRY_HISTORY_INDEX] = current_index - 1
            st.rerun()
    with col_next:
        if st.button("Next", key="next_btn", disabled=current_index >= len(history) - 1, width='stretch'):
            st.session_state[ENTRY_HISTORY_INDEX] = current_index + 1
            st.rerun()

    current_entry = history[current_index]
    st.markdown(f"{current_index + 1}/{len(history)} - {current_entry['query']}")

def render_history(history, dfs) -> None:
    if (len(history) < 2):
        return
    st.write('---')
    st.write('### History')
    for i, entry in enumerate(history):
        if i > 0:
            st.markdown("---")
        st.markdown(f"{'Improvement' if i > 0 else 'Original query'}: {entry['query']}")
        
        render_chart(entry, dfs)
        
        with st.expander("Show generated code", expanded=False):
            st.code(entry["code"])
        
        if st.button(f"Recover", key=f"recover_{i}"):
            st.session_state[ENTRY_HISTORY_INDEX] = i
            st.rerun()