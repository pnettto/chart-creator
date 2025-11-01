from __future__ import annotations

from typing import Dict, Tuple, Optional

import altair as alt
import numpy as np
import pandas as pd
import prophet
import streamlit as st

from llm import ChartCodeGenerator
from constants import (
    CHART_GEN,
    HISTORY_INDEX,
    QUERY,
    SUBMITTED,
)
from ui_components import (
    init_state,
    render_header,
    render_history,
    render_improvement_form,
    render_query_input,
    render_restart_btn,
    render_version_navigation,
)


# =============================
# App bootstrap
# =============================
st.set_page_config(page_title="Natural Chart Creator", layout="wide")


# =============================
# Chart execution
# =============================
def execute_and_display_chart(code_str: str, dfs: Dict[str, pd.DataFrame]) -> st.delta_generator.DeltaGenerator:
    """Execute generated code safely with a restricted global context and show chart.

    Returns the right-hand column container to render controls alongside the chart.
    """
    col_chart, col_controls = st.columns([2, 1])
    with col_chart:
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
            exec(code_str, _globals, {})
        except Exception as e:
            st.write("There was an error")
            st.code(e)
            if st.button("Fix error"):
                chart_gen: ChartCodeGenerator = st.session_state[CHART_GEN]
                result = chart_gen.improve_chart_code(f"Error: {str(e)}")
                success, response_str, dfs = result
                if success and response_str and dfs is not None:
                    execute_and_display_chart(response_str, dfs)
                else:
                    st.write("Error fixing attempt failed.")
            
    return col_controls


# =============================
# Main screen logic
# =============================
def get_current_code_and_dfs(chart_gen: ChartCodeGenerator) -> Tuple[bool, Optional[str], Optional[Dict[str, pd.DataFrame]]]:
    history = chart_gen.get_history()

    # If there's no history yet, generate the initial chart
    if not history:
        result = chart_gen.generate_chart_code(st.session_state[QUERY])
        success, response_str, dfs = result
        if not success:
            return False, response_str, dfs
        # Refresh history after generation and point index to the latest
        history = chart_gen.get_history()
        st.session_state[HISTORY_INDEX] = len(history) - 1

    # Resolve the current entry
    entry = history[st.session_state[HISTORY_INDEX]]

    code_str = entry["improved_code"] if entry.get("improved_code") else entry["code"]
    dfs = chart_gen.dfs
    return True, code_str, dfs


def render_main() -> None:
    init_state()
    render_header()

    if not st.session_state[SUBMITTED]:
        render_query_input()
        return

    # Submitted flow
    st.write(f"Query: {st.session_state[QUERY]}")
    chart_gen: ChartCodeGenerator = st.session_state[CHART_GEN]

    success, code_str, dfs = get_current_code_and_dfs(chart_gen)
    if success and code_str and dfs is not None:
        controls_col = execute_and_display_chart(code_str, dfs)
        with controls_col:
            render_improvement_form(chart_gen)
            render_version_navigation(chart_gen)
            render_restart_btn()
        render_history(chart_gen)
    else:
        st.write("There was an error, try again.")
        if code_str:
            st.code(code_str)
            render_restart_btn()



if __name__ == "__main__":
    render_main()