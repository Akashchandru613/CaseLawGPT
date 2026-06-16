"""
LLM integration for CaseLawGPT.

Provides answer generation using Groq API.
"""
from __future__ import annotations

import os
from typing import List

from groq import Groq

from src.config import GROQ_API_KEY, GROQ_MODEL, MAX_GENERATION_TOKENS


def _get_client() -> Groq:
    key = GROQ_API_KEY or os.getenv("GROQ_API_KEY", "")
    if not key:
        try:
            import streamlit as st
            key = st.secrets.get("GROQ_API_KEY", "")
        except Exception:
            pass
    return Groq(api_key=key)


def build_prompt(question: str, context_chunks: List[str]) -> str:
    numbered_context = "\n\n".join(
        f"[{i + 1}] {chunk}"
        for i, chunk in enumerate(context_chunks)
    )

    return f"""You are CaseLawGPT, a legal research assistant. Answer questions using ONLY the provided case excerpts.

RULES:
- Base your answer strictly on the provided context
- Cite cases by number (e.g., [1], [2]) when making claims
- If the context doesn't contain enough information, say so
- Be precise and legally accurate

CONTEXT FROM RETRIEVED CASES:
{numbered_context}

QUESTION: {question}

ANSWER:"""


def generate_answer(question: str, context_chunks: List[str]) -> str:
    prompt = build_prompt(question, context_chunks)

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=MAX_GENERATION_TOKENS,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"**Error:** {e}"
