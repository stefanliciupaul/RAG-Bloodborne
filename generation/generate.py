"""Calls the generation model via OpenArc's /v1/chat/completions endpoint."""

import re
import requests
import rag_config as cfg

_THINK_BLOCK = re.compile(r"<think>.*?</think>", re.DOTALL)


def build_context_block(chunks: list[dict]) -> str:
    parts = []
    for c in chunks:
        header = f"[{c['page_title']} — {c['section']}]"
        parts.append(f"{header}\n{c['text']}")
    return "\n\n---\n\n".join(parts)


_NO_ANSWER_MSG = (
    "[No answer was generated -> try increasing max_tokens in "
    "rag_config.py, or check whether enable_thinking is set to true.]"
)


def _strip_thinking(text: str) -> str:
    text = _THINK_BLOCK.sub("", text).strip()
    if "<think>" in text:
        return _NO_ANSWER_MSG
    return text if text else _NO_ANSWER_MSG


def _post_chat(question: str, context_chunks: list[dict]) -> str:
    context_block = build_context_block(context_chunks)
    user_message = f"Context:\n{context_block}\n\nQuestion: {question} /no_think"

    r = requests.post(
        f"{cfg.OPENARC_BASE_URL}/chat/completions",
        json={
            "model": cfg.GENERATION_MODEL,
            "messages": [
                {"role": "system", "content": cfg.SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            "chat_template_kwargs": {"enable_thinking": False},
            "max_tokens": 800,
        },
        timeout=180,
    )
    r.raise_for_status()
    return r.json()


def generate_answer(question: str, context_chunks: list[dict]) -> str:
    data = _post_chat(question, context_chunks)
    raw = data["choices"][0]["message"]["content"]
    return _strip_thinking(raw)


def generate_answer_with_metrics(question: str, context_chunks: list[dict]) -> dict:
    # adds OpenArc's usage metrics for the Streamlit frontend
    data = _post_chat(question, context_chunks)
    raw = data["choices"][0]["message"]["content"]
    return {
        "answer": _strip_thinking(raw),
        "usage": data.get("usage", {}),
        "metrics": data.get("metrics", {}),
    }
