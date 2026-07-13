# The frontend for the Bloodborne RAG app.

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "generation"))

import streamlit as st

from retrieve import VectorIndex
from rerank import rerank
from generate import generate_answer_with_metrics
import rag_config as cfg

_ICON_PATH = os.path.join(os.path.dirname(__file__), "..", "bb_hunter_mark.webp")
st.set_page_config(page_title="Bloodborne RAG", page_icon=_ICON_PATH)


@st.cache_resource
def load_index() -> VectorIndex:
    return VectorIndex()


st.title("Bloodborne Strategy Assistant")

with st.spinner(f"Loading index from {cfg.INDEX_PATH}..."):
    index = load_index()
st.caption(f"Loaded {len(index)} chunks.")

if "messages" not in st.session_state:
    st.session_state.messages = []


def render_sources(sources: list[dict]) -> None:
    with st.expander("Sources"):
        for s in sources:
            score = (
                f" (score {s['rerank_score']:.3f})"
                if s["rerank_score"] is not None
                else ""
            )
            snippet = s.get("text", "")[:200].replace("\n", " ")
            st.markdown(f"**{s['page_title']} / {s['section']}**{score}")
            st.caption(f'"{snippet}..."')


def render_stats(metrics: dict) -> None:
    if not metrics:
        return
    tps = metrics.get("decode_throughput (tokens/s)")
    new_tokens = metrics.get("new_token")
    ttft = metrics.get("ttft (s)")
    bits = []
    if new_tokens is not None:
        bits.append(f"{new_tokens} tokens")
    if tps is not None:
        bits.append(f"{tps:.1f} tok/s")
    if ttft is not None:
        bits.append(f"ttft {ttft:.2f}s")
    if bits:
        st.caption(" · ".join(bits))


for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant":
            if msg.get("sources"):
                render_sources(msg["sources"])
            render_stats(msg.get("metrics", {}))

question = st.chat_input("Ask a question about Bloodborne...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.status(
            "Embedding question & retrieving candidates...", expanded=False
        ) as status:
            candidates = index.search(question, top_k=cfg.RETRIEVE_TOP_K)

            status.update(label=f"Retrieved {len(candidates)} candidates. Reranking...")
            top_chunks = rerank(question, candidates, top_k=cfg.RERANK_TOP_K)

            status.update(
                label=f"Reranked to top {len(top_chunks)} chunks. Generating answer..."
            )
            gen = generate_answer_with_metrics(question, top_chunks)

            status.update(label="Done", state="complete")

        st.markdown(gen["answer"])

        sources = [
            {
                "page_title": c["page_title"],
                "section": c["section"],
                "url": c.get("url"),
                "text": c.get("text", ""),
                "rerank_score": c.get("rerank_score"),
            }
            for c in top_chunks
        ]
        if sources:
            render_sources(sources)
        render_stats(gen["metrics"])

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": gen["answer"],
            "sources": sources,
            "metrics": gen["metrics"],
        }
    )
