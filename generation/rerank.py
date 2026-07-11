"""Reranks retrieved candidates via OpenArc's /v1/rerank endpoint, keyed on
the response shape confirmed earlier:
{"data": [{"index": 0, "ranked_documents": {"doc": "...", "score": 0.99}}, ...]}
"""

import requests
import rag_config as cfg


def rerank(
    query: str, candidates: list[dict], top_k: int = cfg.RERANK_TOP_K
) -> list[dict]:
    if not candidates:
        return []

    documents = [c["text"] for c in candidates]
    r = requests.post(
        f"{cfg.OPENARC_BASE_URL}/rerank",
        json={"model": cfg.RERANK_MODEL, "query": query, "documents": documents},
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()["data"]

    scored = []
    for entry in data:
        idx = entry["index"]
        score = entry["ranked_documents"]["score"]
        rec = dict(candidates[idx])
        rec["rerank_score"] = score
        scored.append(rec)

    # sort the docs in descending order based on cross-encoder score
    scored.sort(key=lambda r: r["rerank_score"], reverse=True)
    return scored[:top_k]
