"""Combines the retrieval, reranking, and generation parts into one RAG query function."""

from retrieve import VectorIndex
from rerank import rerank
from generate import generate_answer
import rag_config as cfg


def answer_question(index: VectorIndex, question: str) -> dict:
    candidates = index.search(question, top_k=cfg.RETRIEVE_TOP_K)
    top_chunks = rerank(question, candidates, top_k=cfg.RERANK_TOP_K)
    answer = generate_answer(question, top_chunks)

    return {
        "answer": answer,
        "sources": [
            {
                "page_title": c["page_title"],
                "section": c["section"],
                "url": c.get("url"),
                "text": c.get("text", ""),
                "rerank_score": c.get("rerank_score"),
            }
            for c in top_chunks
        ],
    }
