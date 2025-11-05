from __future__ import annotations

import altair as alt
import numpy as np
import pandas as pd
import prophet
import streamlit as st

from constants import (
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


def render_improvement_form() -> None:
    def update_improvement_query():
        st.session_state[IMPROVEMENT_QUERY] = st.session_state['current_improvement_query_value']
        st.session_state['trigger_rerun_improvement'] = True

    st.text_area("Ask for an improvement", key='current_improvement_query_value')
    if st.button("Submit"):
        update_improvement_query()

    if st.session_state.get('trigger_rerun_improvement', False):
        st.session_state['trigger_rerun_improvement'] = False 
        st.rerun()