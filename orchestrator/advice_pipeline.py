from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq


SUB_QUESTION_PATH = Path(__file__).with_name("sub-question.py")
MODEL_NAME = "llama-3.3-70b-versatile"


@lru_cache(maxsize=1)
def _load_sub_question_function():
    """Load the existing helper without running its example block."""
    source = SUB_QUESTION_PATH.read_text(encoding="utf-8")
    marker = "# Example Usage:"
    if marker in source:
        source = source.split(marker, 1)[0]

    namespace: dict[str, object] = {}
    exec(compile(source, str(SUB_QUESTION_PATH), "exec"), namespace)

    generate_sub_questions = namespace.get("generate_sub_questions")
    if not callable(generate_sub_questions):
        raise RuntimeError("Could not load generate_sub_questions from sub-question.py")

    return generate_sub_questions


def _build_groq_client() -> Groq:
    load_dotenv()
    api_key = os.getenv("GROQ_API")
    if not api_key:
        raise RuntimeError("Missing GROQ_API in your environment.")
    return Groq(api_key=api_key)


def generate_financial_advice(client_email: str) -> str:
    """Turn a pasted client email into an advisor-ready response draft."""
    email_text = client_email.strip()
    if not email_text:
        raise ValueError("Please paste a client email before generating advice.")

    generate_sub_questions = _load_sub_question_function()
    sub_questions = generate_sub_questions(email_text)
    groq_client = _build_groq_client()

    system_prompt = """
    You are an experienced financial advisor drafting a client-ready reply.
    Use the client's email and the analysis questions below to write a concise,
    practical response. Keep the tone professional and helpful, avoid hype,
    acknowledge uncertainty, and never invent portfolio-specific facts that
    were not provided.

    Output:
    1. A short "Recommended response" addressed to the client.
    2. A brief "Advisor notes" section with the key reasoning.
    """

    completion = groq_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": system_prompt.strip()},
            {
                "role": "user",
                "content": (
                    f"Client email:\n{email_text}\n\n"
                    f"Analysis questions:\n{sub_questions}"
                ),
            },
        ],
    )

    return completion.choices[0].message.content.strip()
