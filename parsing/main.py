"""
Extracting content from the Bloodborne Wiki (bloodborne-wiki.com)"""

import json
from pathlib import Path

import config
from fetcher import fetch_all
from parser import get_page_title, extract_sections
from chunker import chunk_section, filter_sections_by_allowlist, dedupe_sections
from boilerplate import strip_cross_page_boilerplate
from reformat import reformat_weak_points


def _embedding_label(heading: str) -> str:
    """
    The label prepended to a chunk's text for embedding
    purposes "Weak Points" becomes "Breakable body parts"
    """
    if "weak point" in heading.lower():
        return "Breakable body parts and damage thresholds"
    return heading


def build_page_list() -> list[str]:
    urls = list(config.PAGE_URLS)
    return urls


def main():
    urls = build_page_list()
    pages_html = fetch_all(urls)

    # parse the url list in config.py
    page_sections: dict[str, list[tuple[str, str]]] = {}
    page_url: dict[str, str] = {}

    for url, html in pages_html.items():
        title = get_page_title(html)
        try:
            sections = extract_sections(html)
        except ValueError as e:
            print(f"  [skip] {url}: {e}")
            continue

        sections = dedupe_sections(sections)
        sections = filter_sections_by_allowlist(sections, config.SECTION_ALLOWLIST)

        # Reformats the Weak Points table into natural-language sentences
        sections = [
            (
                heading,
                reformat_weak_points(text) if "weak point" in heading.lower() else text,
            )
            for heading, text in sections
        ]

        page_sections[title] = sections
        page_url[title] = url
        print(
            f"Parsed '{title}': {len(sections)} sections kept "
            f"({[h for h, _ in sections]})"
        )

    # Pass 2: strip paragraphs that repeat verbatim across many pages
    before = sum(len(t) for secs in page_sections.values() for _, t in secs)
    page_sections = strip_cross_page_boilerplate(
        page_sections,
        min_pages=config.BOILERPLATE_MIN_PAGES,
        min_fraction=config.BOILERPLATE_MIN_FRACTION,
        heading_categories=config.SECTION_ALLOWLIST,
    )
    after = sum(len(t) for secs in page_sections.values() for _, t in secs)
    print(
        f"\nBoilerplate stripping: {before} -> {after} chars "
        f"({before - after} chars removed)"
    )

    # chunk and write to jsonl file
    all_records = []
    for title, sections in page_sections.items():
        for heading, text in sections:
            label = _embedding_label(heading)
            for chunk in chunk_section(text, config.MAX_CHUNK_CHARS):
                all_records.append(
                    {
                        "page_title": title,
                        "section": heading,
                        "url": page_url[title],
                        "text": chunk,
                        "embed_text": f"{label}: {chunk}",
                    }
                )

    out_path = Path(config.OUTPUT_PATH)
    with out_path.open("w", encoding="utf-8") as f:
        for rec in all_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"\nWrote {len(all_records)} chunks to {out_path.resolve()}")


if __name__ == "__main__":
    main()
