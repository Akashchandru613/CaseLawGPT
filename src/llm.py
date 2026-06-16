"""
LLM integration for CaseLawGPT.

Supports two backends, selected via LLM_BACKEND env var:
  - "ollama" (default): local model via Ollama, works on GPU-equipped HPC
  - "groq": cloud API, works on any machine without GPU
"""
from __future__ import annotations

from typing import List

import requests

from src.config import (
    LLM_BACKEND,
    OLLAMA_MODEL, OLLAMA_URL,
    GROQ_API_KEY, GROQ_MODEL,
    MAX_GENERATION_TOKENS,
)


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


def _generate_ollama(prompt: str) -> str:
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": OLLAMA_MODEL,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.3,
                    "num_predict": MAX_GENERATION_TOKENS,
                },
            },
            timeout=120,
        )
        response.raise_for_status()
        return response.json().get("response", "").strip()
    except requests.exceptions.ConnectionError:
        return "**Error:** Cannot connect to Ollama. Run `ollama serve` first."
    except requests.exceptions.Timeout:
        return "**Error:** Request timed out. Try again."
    except Exception as e:
        return f"**Error:** {e}"


def _generate_groq(prompt: str) -> str:
    try:
        from groq import Groq

        key = GROQ_API_KEY
        if not key:
            try:
                import streamlit as st
                key = st.secrets.get("GROQ_API_KEY", "")
            except Exception:
                pass

        client = Groq(api_key=key)
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=MAX_GENERATION_TOKENS,
            temperature=0.3,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"**Error:** {e}"


def generate_answer(question: str, context_chunks: List[str]) -> str:
    prompt = build_prompt(question, context_chunks)
    if LLM_BACKEND == "groq":
        return _generate_groq(prompt)
    return _generate_ollama(prompt)
