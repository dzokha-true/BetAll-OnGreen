from __future__ import annotations

import streamlit as st

from orchestrator.advice_pipeline import generate_financial_advice


st.set_page_config(page_title="Client Email Advisor", layout="wide")
st.title("Client Email Advisor")
st.caption("Paste a client email on the left and generate a draft response on the right.")

if "advice_output" not in st.session_state:
    st.session_state.advice_output = ""

left_col, right_col = st.columns(2)

with left_col:
    client_email = st.text_area(
        "Client Email",
        height=420,
        placeholder="Paste the client's email here...",
    )

    if st.button("Generate Advice", type="primary", use_container_width=True):
        try:
            with st.spinner("Generating financial advice..."):
                st.session_state.advice_output = generate_financial_advice(client_email)
        except Exception as exc:
            st.error(str(exc))

with right_col:
    st.text_area(
        "Financial Advice Output",
        value=st.session_state.advice_output,
        height=420,
        disabled=True,
        placeholder="Generated advice will appear here...",
    )
