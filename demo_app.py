from __future__ import annotations

import re
import time

import streamlit as st


def extract_name(prompt: str) -> str:
    match = re.search(r"\bi am\s+([A-Za-z]+(?:\s+[A-Za-z]+){0,2})", prompt, re.IGNORECASE)
    return match.group(1).strip() if match else "there"


def extract_stock(prompt: str) -> str:
    patterns = [
        r"sell\s+my\s+([A-Za-z][A-Za-z0-9&.\-\s]+?)\s+stocks?\b",
        r"my\s+([A-Za-z][A-Za-z0-9&.\-\s]+?)\s+stocks?\b",
        r"sell\s+([A-Za-z][A-Za-z0-9&.\-\s]+?)\s+stocks?\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            return match.group(1).strip().title()

    return "Nvidia"


def build_demo_response(prompt: str) -> str:
    name = extract_name(prompt)
    stock = extract_stock(prompt)

    return (
        f"Subject: Recommendation on Your {stock} Position\n\n"
        f"Hi {name},\n\n"
        f"Thanks for reaching out. Based on current sentiment, our SnowLeopard signal, "
        f"and the latest internal market read, my recommendation is that you **do not sell "
        f"your {stock} shares at this time**.\n\n"
        f"Here is the reasoning:\n"
        f"- Current sentiment remains constructive.\n"
        f"- Our internal data still favors holding over exiting today.\n"
        f"- Near-term momentum does not currently suggest an urgent sell signal.\n\n"
        f"Recommended client reply:\n"
        f"At this stage, we would recommend holding your {stock} position rather than selling. "
        f"Based on current sentiment and our latest analysis, the data does not support exiting "
        f"the position right now unless your liquidity needs or risk tolerance have changed.\n\n"
        f"Best,\n"
        f"Your Advisor"
    )


st.set_page_config(page_title="SnowLeopard Demo", layout="centered")
st.title("SnowLeopard Investor Copilot")
st.caption("Presentation demo with a simulated sentiment and market intelligence workflow.")

if "demo_response" not in st.session_state:
    st.session_state.demo_response = ""

if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""

st.info("Ask a client-style question and the app will simulate querying SnowLeopard before returning a recommendation.")

with st.form("demo_form"):
    user_prompt = st.text_area(
        "Client question",
        height=140,
    )
    submitted = st.form_submit_button("Ask SnowLeopard", type="primary", use_container_width=True)

if submitted:
    if not user_prompt.strip():
        st.error("Enter a client-style question to run the demo.")
    else:
        progress_text = st.empty()
        progress_bar = st.progress(0)

        steps = [
            "Connecting to SnowLeopard...",
            "Checking real-time market sentiment...",
            "Reviewing portfolio intelligence and internal signals...",
            "Drafting recommendation...",
        ]

        for index, step in enumerate(steps, start=1):
            progress_text.markdown(f"**{step}**")
            progress_bar.progress(index * 25)
            time.sleep(0.9)

        st.session_state.last_prompt = user_prompt
        st.session_state.demo_response = build_demo_response(user_prompt)
        progress_text.empty()
        progress_bar.empty()

if st.session_state.demo_response:
    st.subheader("Recommendation")
    st.write(st.session_state.demo_response)

    with st.expander("Demo input"):
        st.write(st.session_state.last_prompt)
