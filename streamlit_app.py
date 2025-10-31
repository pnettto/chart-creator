
import altair as alt
import numpy as np
import pandas as pd
import prophet
import streamlit as st

from llm import ChartCodeGenerator


st.set_page_config(page_title="Natural Chart Creator", layout="wide")
st.title("Natural Chart Creator")

if "chart_gen" not in st.session_state:
    st.session_state.chart_gen = ChartCodeGenerator()
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "query" not in st.session_state:
    st.session_state.query = ""

if not st.session_state.submitted:
    query = st.text_input("Enter your query", key="query_input")
    if st.button("Submit", use_container_width=True) or (query and st.session_state.query_input):
        st.session_state.submitted = True
        st.session_state.query = query or st.session_state.query_input
else:
    st.write(f"Query: **{st.session_state.query}**")

    chart_gen = st.session_state.chart_gen

    if not st.session_state.get("show_improved", False):
        success, response_str, dfs = chart_gen.generate_chart_code(st.session_state.query)
        st.session_state.last_code = response_str if success else None
        st.session_state.last_dfs = dfs if success else None
    else:
        # If improved, use the improved code
        success = True
        response_str = chart_gen.current_code
        dfs = chart_gen.dfs

    if success:
        code_str = response_str
        col1, col2 = st.columns([2, 1])
        with col1:
            try:
                exec(code_str, globals(), locals())
            except Exception as e:
                st.write(f'There was an error, try again.')
                st.code(e)
        with col2:
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

            if st.button("Try again", key="try_again_btn", use_container_width=True):
                st.session_state.show_improved = False
                st.rerun()

            if st.button("Restart", key="restart_btn", use_container_width=True):
                st.session_state.submitted = False
                st.session_state.query = ""
                st.session_state.improvement_text_value = ""
                st.session_state.show_improved = False
        
        with st.expander("Show generated code", expanded=False):
                st.code(code_str)
        
        # Optionally show history
        with st.expander("Show improvement history", expanded=False):
            for i, entry in enumerate(chart_gen.get_history()):
                if i > 0:
                    st.markdown(f"---")
                st.markdown(f"**Step {i+1}:**")
                if entry['improvement_query']:
                    st.markdown(f"- Improvement: {entry['improvement_query']}")
                with st.expander("Show generated code", expanded=False):
                    st.code(entry['improved_code'] if entry['improved_code'] else entry['code'])
                if st.button(f"Recover", key=f"recover_{i}"):
                    # Set the current code to this improvement and rerun
                    chart_gen.current_code = entry['improved_code'] if entry['improved_code'] else entry['code']
                    st.session_state.show_improved = True
                    st.session_state.improvement_text_value = entry.get('improvement_query', '')
                    st.rerun()
    else:
        st.write('There was an error, try again. Code: 002.')
        st.code(response_str)