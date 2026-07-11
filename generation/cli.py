"""
CLI interface for the RAG application

"""

from retrieve import VectorIndex
from rag import answer_question
import rag_config as cfg


def main():
    print(f"Loading index from {cfg.INDEX_PATH}...")
    index = VectorIndex()
    print(f"Loaded {len(index)} chunks. Ask a question (Ctrl+C to quit).\n")

    while True:
        try:
            question = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue

        result = answer_question(index, question)
        print(f"\n{result['answer']}\n")
        print("Sources:")
        for s in result["sources"]:
            score = (
                f" (score {s['rerank_score']:.3f})"
                if s["rerank_score"] is not None
                else ""
            )
            snippet = s.get("text", "")[:60].replace("\n", " ")
            print(f"  - {s['page_title']} / {s['section']}{score}")
            print(f'      "{snippet}..."')
        print()


if __name__ == "__main__":
    main()
