"""
Detects and strips paragraphs that repeat exactly across many different
pages under the same heading -> In this the Weak Points paragraphs are
specifically targeted. This has to run as a separate pass after all pages
have been parsed
"""

from collections import defaultdict


def _split_paragraphs(text: str) -> list[str]:
    return [p.strip() for p in text.split("\n") if p.strip()]


def _normalize_heading(heading: str, categories: list[str] | None) -> str:
    """
    Headings normalize to a category (Cleric Beast Weak Points becomes just Weak Points
    Falls back to the heading itself unchanged if no category matches, or if no categories were given.
    """
    if not categories:
        return heading
    lower = heading.lower()
    for cat in categories:
        if cat.lower() in lower:
            return cat.lower()
    return heading


def strip_cross_page_boilerplate(
    pages: dict[str, list[tuple[str, str]]],
    min_pages: int = 3,
    min_fraction: float = 0.5,
    heading_categories: list[str] | None = None,
) -> dict[str, list[tuple[str, str]]]:
    """
    pages: {page_title: [(heading, text), ...]}
    A paragraph is treated as boilerplate for a given heading CATEGORY if it
    appears exactly the same on at least `min_pages` different pages and on at
    least `min_fraction` (in config.py) of all pages that have that category at all.
    Returns the same {page_title: [(heading, text), ...]} shape with boilerplate
    paragraphs removed. A section that becomes empty after stripping (which means it
    was ONLY boilerplate) is dropped entirely.
    """
    paragraph_pages: dict[str, dict[str, set[str]]] = defaultdict(
        lambda: defaultdict(set)
    )
    pages_with_category: dict[str, set[str]] = defaultdict(set)

    for page_title, sections in pages.items():
        for heading, text in sections:
            key = _normalize_heading(heading, heading_categories)
            pages_with_category[key].add(page_title)
            for para in _split_paragraphs(text):
                paragraph_pages[key][para].add(page_title)

    boilerplate: dict[str, set[str]] = defaultdict(set)
    for key, para_map in paragraph_pages.items():
        total = len(pages_with_category[key])
        for para, page_set in para_map.items():
            if len(page_set) >= min_pages and len(page_set) / total >= min_fraction:
                boilerplate[key].add(para)

    cleaned: dict[str, list[tuple[str, str]]] = {}
    for page_title, sections in pages.items():
        new_sections = []
        for heading, text in sections:
            key = _normalize_heading(heading, heading_categories)
            kept = [p for p in _split_paragraphs(text) if p not in boilerplate[key]]
            new_text = "\n\n".join(kept)
            if new_text.strip():
                new_sections.append((heading, new_text))
        cleaned[page_title] = new_sections

    return cleaned
