import json
import datetime
import streamlit as st

from streamlit_js_eval import streamlit_js_eval

from constants import (
    ENTRY_HISTORY_INDEX,
    LOCAL_STORAGE_HISTORY,
    ORIGINAL_QUERY,
)

from ui_components import (
    render_chart
)

def render_chart_history(history, dfs) -> None:
    if (len(history) == 0):
        return
    
    st.write('---')
    st.write('### History')
    with st.expander("Show", expanded=False):
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

def sync_local_storage_history_to_session():
    result = streamlit_js_eval(
        js_expressions="localStorage.getItem('chart_histories')",
        key="get_chart_histories"
    )
    if result is None:
        st.session_state[LOCAL_STORAGE_HISTORY] = None
        st.rerun()
    else:
        st.session_state[LOCAL_STORAGE_HISTORY] = result

def render_local_storage_history_recovering_tool_load(chart_gen):
    # Load histories from localStorage
    existing_history = st.session_state[LOCAL_STORAGE_HISTORY]
    if existing_history:
        try:
            history = json.loads(existing_history)
        except Exception as e:
            st.error(f"Error parsing chart_histories: {e}")
            history = []
    else:
        history = []

    if history:
        col_l, _ = st.columns([3, 1])
        with col_l:
            st.markdown('---')
            st.markdown('### Load a previous exploration')
            selected_index = st.selectbox(
                label="Select",
                options=list(range(len(history))),
                format_func=lambda idx: (
                    f"{datetime.datetime.fromisoformat(history[idx]['date']).strftime('%Y-%m-%d@%H:%M')}: "
                    f"{history[idx]['history'][0]['query']}"
                ),
            )
            if st.button("Load", key="load_history_btn"):
                selected_history_item = history[selected_index]
                chart_gen.history = selected_history_item['history']
                st.session_state[ORIGINAL_QUERY] = selected_history_item['history'][0]['query']
                st.rerun()

def render_local_storage_recovering_tool_save(chart_gen):
    if st.button("Save current exploration", key="save_history_btn"):
        try:
            existing_history = st.session_state[LOCAL_STORAGE_HISTORY]
            history = json.loads(existing_history)
        except:
            history = []
    
        new_history_data = {
            "date": datetime.datetime.now().isoformat(),
            "history": chart_gen.history,
        }

        history.sort(key=lambda x: x["date"], reverse=True)

        history.append(new_history_data)
        safe_history_json = json.dumps(history)
        escaped_json = safe_history_json.replace("\\", "\\\\").replace("'", "\\'")
        st.success("Saved")
        streamlit_js_eval(
            js_expressions=f"localStorage.setItem('chart_histories', '{escaped_json}')",
            key="set_chart_histories"
        )
        st.session_state[LOCAL_STORAGE_HISTORY] = safe_history_json
        st.rerun()
