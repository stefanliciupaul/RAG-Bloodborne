"""
Starting from the wiki_chunks.jsonl it creates the local vector index by embedding every chunk
through OpenArc's /v1/embeddings endpoint using numpy.
"""

import json
import numpy as np
import requests

import rag_config as cfg


def embed_text(text: str) -> list[float]:
    r = requests.post(
        f"{cfg.OPENARC_BASE_URL}/embeddings",
        json={"model": cfg.EMBED_MODEL, "input": text},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["data"][0]["embedding"]


def load_chunks(chunks_path: str) -> list[dict]:
    records = []
    with open(chunks_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def build_index(chunks_path: str = cfg.CHUNKS_PATH, index_path: str = cfg.INDEX_PATH):
    records = load_chunks(chunks_path)
    print(f"Embedding {len(records)} chunks...")

    vectors, kept_records = [], []
    for i, rec in enumerate(records):
        try:
            # adding a  label for embedding
            text_to_embed = rec.get("embed_text", rec["text"])
            vectors.append(embed_text(text_to_embed))
            kept_records.append(rec)
        except requests.RequestException as e:
            print(
                f"  [skip] chunk {i} ({rec.get('page_title')}/{rec.get('section')}): {e}"
            )

        if (i + 1) % 25 == 0 or (i + 1) == len(records):
            print(f"  {i + 1}/{len(records)}")

    vectors = np.array(vectors, dtype=np.float32)

    np.savez(
        index_path,
        vectors=vectors,
        metadata=np.array([json.dumps(r) for r in kept_records], dtype=object),
    )
    print(
        f"\nWrote index to {index_path} "
        f"({vectors.shape[0]} vectors, dim={vectors.shape[1] if vectors.size else 0})"
    )


if __name__ == "__main__":
    build_index()
