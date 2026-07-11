"""Loads the vector index built by embed_store.py and performs cosine-
similarity retrieval against it."""

import json
import numpy as np

import rag_config as cfg
from embed_store import embed_text


class VectorIndex:
    def __init__(self, index_path: str = cfg.INDEX_PATH):
        data = np.load(index_path, allow_pickle=True)
        self.vectors = data["vectors"]
        self.metadata = [json.loads(m) for m in data["metadata"]]

        norms = np.linalg.norm(self.vectors, axis=1, keepdims=True)
        norms[norms == 0] = 1e-8  # avoid division by 0 when the vector is empty
        self._normed = self.vectors / norms

    def __len__(self):
        return len(self.metadata)

    def search(self, query: str, top_k: int = cfg.RETRIEVE_TOP_K) -> list[dict]:
        q_vec = np.array(embed_text(query), dtype=np.float32)
        q_norm = q_vec / (np.linalg.norm(q_vec) or 1e-8)

        scores = self._normed @ q_norm
        top_idx = np.argsort(-scores)[:top_k]

        results = []
        for idx in top_idx:
            rec = dict(self.metadata[idx])
            rec["score"] = float(scores[idx])
            results.append(rec)
        return results
