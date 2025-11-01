from __future__ import annotations

from typing import TYPE_CHECKING

import streamlit as st

from llm import ChartCodeGenerator
from constants import (
    CHART_GEN,
    SUBMITTED,
    QUERY,
    IMPROVEMENT_TEXT_VALUE,
    HISTORY_INDEX,
)

def render_header() -> None:
    st.title("Natural Chart Creator")


def render_query_input() -> None:
    """Query input and submit button. Sets session state when submitted."""
    query = st.text_input("Enter your query", key="query_input")
    submitted = st.button("Submit", use_container_width=True)
    if submitted or (query or st.session_state.query_input):
        st.session_state[SUBMITTED] = True
        st.session_state[QUERY] = query or st.session_state.query_input


def render_improvement_form(chart_gen: ChartCodeGenerator) -> None:
    """Form for requesting improvements to the generated chart code."""
    with st.form("improvement_form"):
        improvement_text = st.text_area("Ask for an improvement", key="improvement_text")
        submitted = st.form_submit_button("Submit")
        if submitted and improvement_text:
            improve_success, improved_code, _dfs = chart_gen.improve_chart_code(improvement_text)
            if improve_success:
                st.session_state[IMPROVEMENT_TEXT_VALUE] = improvement_text
                # Keep current HISTORY_INDEX so the current chart remains visible.
                # Rerun to refresh controls (Next will become enabled if a new version exists).
                st.rerun()
            else:
                st.write("Improvement failed:")
                st.code(improved_code)


def render_version_navigation(chart_gen: ChartCodeGenerator) -> None:
    """Prev/Next navigation for code versions with current version info."""
    history = chart_gen.get_history()
    if HISTORY_INDEX not in st.session_state:
        st.session_state[HISTORY_INDEX] = len(history) - 1

    col_prev, col_next = st.columns([1, 1])
    with col_prev:
        if st.button(
            "Prev",
            key="prev_btn",
            use_container_width=True,
            disabled=st.session_state[HISTORY_INDEX] <= 0,
        ):
            st.session_state[HISTORY_INDEX] = max(0, st.session_state[HISTORY_INDEX] - 1)
            st.rerun()
    with col_next:
        if st.button(
            "Next",
            key="next_btn",
            use_container_width=True,
            disabled=st.session_state[HISTORY_INDEX] >= len(history) - 1,
        ):
            st.session_state[HISTORY_INDEX] = min(
                len(history) - 1, st.session_state[HISTORY_INDEX] + 1
            )
            st.rerun()

    entry = history[st.session_state[HISTORY_INDEX]]
    st.markdown(
        f"{st.session_state[HISTORY_INDEX] + 1}/{len(history)} - "
        f"{entry['improvement_query'] if entry['improvement_query'] else st.session_state[QUERY]}"
    )

def render_history(chart_gen: ChartCodeGenerator) -> None:
    """Expandable history of generated/improved code with recover buttons."""
    with st.expander("Show history", expanded=False):
        history = chart_gen.get_history()
        for i, entry in enumerate(history):
            if i > 0:
                st.markdown("---")
            if entry["improvement_query"]:
                st.markdown(f"Improvement: {entry['improvement_query']}")
            else:
                st.markdown(f"Original query: {st.session_state[QUERY]}")
            with st.expander("Show generated code", expanded=False):
                st.code(entry["improved_code"] if entry["improved_code"] else entry["code"])
            if st.button(f"Recover", key=f"recover_{i}"):
                st.session_state[HISTORY_INDEX] = i
                st.rerun()


def render_restart_btn() -> None:
    if st.button("Restart", key="restart_btn", use_container_width=True):
        # Fully reset state and generator
        st.session_state[SUBMITTED] = False
        st.session_state[QUERY] = ""
        st.session_state[IMPROVEMENT_TEXT_VALUE] = ""
        if HISTORY_INDEX in st.session_state:
            del st.session_state[HISTORY_INDEX]
        st.session_state[CHART_GEN] = ChartCodeGenerator()
        st.rerun()


def init_state() -> None:
    st.session_state.setdefault(IMPROVEMENT_TEXT_VALUE, "")
    st.session_state.setdefault(QUERY, "")
    st.session_state.setdefault(SUBMITTED, False)
    # Persist a single ChartCodeGenerator instance across reruns without
    # constructing unnecessary instances on each rerun
    if CHART_GEN not in st.session_state:
        st.session_state[CHART_GEN] = ChartCodeGenerator()
