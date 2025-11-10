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