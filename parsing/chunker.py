"""Splitting the sections in the text according to the chunk size."""

import re

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _split_long_paragraph(para: str, max_chars: int) -> list[str]:
    """for section where a single paragraph that alone exceeds max_chars and has
    no internal newline to break on"""
    sentences = _SENTENCE_SPLIT.split(para)
    chunks, current = [], ""
    for sent in sentences:
        if len(current) + len(sent) + 1 > max_chars and current:
            chunks.append(current.strip())
            current = sent
        else:
            current = f"{current} {sent}" if current else sent
    if current.strip():
        chunks.append(current.strip())
    return chunks


def _word_set(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def dedupe_sections(
    sections: list[tuple[str, str]], threshold: float = 0.85
) -> list[tuple[str, str]]:
    """
    drop sections that are near-duplicates of an earlier one under the same
    heading
    """
    kept: list[tuple[str, str]] = []
    seen_by_heading: dict[str, list[set[str]]] = {}

    for heading, text in sections:
        words = _word_set(text)
        prior = seen_by_heading.setdefault(heading, [])

        is_dupe = False
        for other_words in prior:
            if not words or not other_words:
                continue
            overlap = len(words & other_words) / min(len(words), len(other_words))
            if overlap >= threshold:
                is_dupe = True
                break

        if not is_dupe:
            kept.append((heading, text))
            prior.append(words)

    return kept


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
        (heading, text)
        for heading, text in sections
        if any(k in heading.lower() for k in keywords)
    ]


def chunk_section(text: str, max_chars: int) -> list[str]:
    if len(text) <= max_chars:
        return [text]

    paragraphs = [p for p in text.split("\n") if p.strip()]
    chunks, current = [], ""
    for para in paragraphs:
        if len(para) > max_chars:
            if current:
                chunks.append(current.strip())
                current = ""
            chunks.extend(_split_long_paragraph(para, max_chars))
            continue

        if len(current) + len(para) + 1 > max_chars and current:
            chunks.append(current.strip())
            current = para
        else:
            current = f"{current}\n{para}" if current else para
    if current.strip():
        chunks.append(current.strip())
    return chunks
