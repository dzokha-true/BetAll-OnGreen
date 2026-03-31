from __future__ import annotations

import streamlit as st

from orchestrator.grok_function_agent import run_agent


st.set_page_config(page_title="Tech Market Orchestrator", layout="wide")
st.title("Tech Market Orchestrator")
st.caption("Ask for a market report or follow-up analysis powered by the orchestrator agent.")

if "agent_output" not in st.session_state:
    st.session_state.agent_output = ""

if "tool_outputs" not in st.session_state:
    st.session_state.tool_outputs = {}

left_col, right_col = st.columns(2)

with left_col:
    user_prompt = st.text_area(
        "Request",
        height=420,
        placeholder="Example: Generate a tech market report for today and explain the biggest movers.",
    )

    if st.button("Run Orchestrator", type="primary", use_container_width=True):
        try:
            with st.spinner("Running orchestrator..."):
                answer, state = run_agent(user_prompt)
                st.session_state.agent_output = answer
                st.session_state.tool_outputs = state.tool_outputs
        except Exception as exc:
            st.error(str(exc))

with right_col:
    st.text_area(
        "Orchestrator Output",
        value=st.session_state.agent_output,
        height=420,
        disabled=True,
        placeholder="The orchestrator response will appear here...",
    )

if st.session_state.tool_outputs:
    with st.expander("Tool Call Details"):
        st.json(st.session_state.tool_outputs)
