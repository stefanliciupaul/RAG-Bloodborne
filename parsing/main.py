"""
Extracting content from the Bloodborne Wiki (bloodborne-wiki.com)"""

import json
from pathlib import Path

import config
from fetcher import fetch_all
from parser import get_page_title, extract_sections
from chunker import chunk_section, filter_sections_by_allowlist


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

        sections = filter_sections_by_allowlist(sections, config.SECTION_ALLOWLIST)

        page_sections[title] = sections
        page_url[title] = url
        print(
            f"Parsed '{title}': {len(sections)} sections kept "
            f"({[h for h, _ in sections]})"
        )

    # chunk and write to jsonl file
    all_records = []
    for title, sections in page_sections.items():
        for heading, text in sections:
            for chunk in chunk_section(text, config.MAX_CHUNK_CHARS):
                all_records.append(
                    {
                        "page_title": title,
                        "section": heading,
                        "url": page_url[title],
                        "text": chunk,
                    }
                )

    out_path = Path(config.OUTPUT_PATH)
    with out_path.open("w", encoding="utf-8") as f:
        for rec in all_records:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print(f"\nWrote {len(all_records)} chunks to {out_path.resolve()}")


if __name__ == "__main__":
    main()
