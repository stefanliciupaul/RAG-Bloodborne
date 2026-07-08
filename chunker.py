"""Splitting the sections in the text according to the chunk size."""

import re


def _word_set(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))

def filter_sections_by_allowlist(
    sections: list[tuple[str, str]], allowlist: list[str]
) -> list[tuple[str, str]]:
    """
    keep only sections whose heading matches one of the allowlist keywords in config file
    """
    if not allowlist:
        return sections
    keywords = [k.lower() for k in allowlist]
    return [
        (heading, text) for heading, text in sections
        if any(k in heading.lower() for k in keywords)
    ]


def chunk_section(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]

    paragraphs = [p for p in text.split("\n") if p.strip()]
    chunks, current = [], ""
    for para in paragraphs:
        if len(current) + len(para) + 1 > max_chars and current:
            chunks.append(current.strip())
            current = para
        else:
            current = f"{current}\n{para}" if current else para
    if current.strip():
        chunks.append(current.strip())
    return chunks
