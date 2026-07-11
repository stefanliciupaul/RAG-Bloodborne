"""
Parser for the bloodborne-wiki.com
"""

from bs4 import BeautifulSoup, Tag

POST_BODY_SELECTORS = [
    ("div", {"class": "post-body"}),
    ("div", {"class": "entry-content"}),
    ("article", {}),
]

CONTENT_TAGS = ["h3", "li", "i", "tr"]
_UI_NOISE_MARKERS = ("click to expand", "click to collapse")


def get_page_title(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    if soup.title and soup.title.string:
        return soup.title.string.split("|")[0].strip()
    return "Unknown Page"


def _find_post_body(soup: BeautifulSoup) -> Tag:
    for tag_name, attrs in POST_BODY_SELECTORS:
        found = soup.find(tag_name, attrs=attrs)
        if found is not None:
            return found
    raise ValueError()


def _row_text(tr: Tag) -> str | None:
    # Flatten a <tr>'s own direct cells into one pipe-delimited line.
    cells = [
        c.get_text(separator=" ", strip=True)
        for c in tr.find_all(["td", "th"], recursive=False)
    ]
    cells = [c for c in cells if c]
    if len(cells) > 1:
        line = " | ".join(cells)
        if any(marker in line.lower() for marker in _UI_NOISE_MARKERS):
            return None
        return line
    return None


def extract_sections(html: str) -> list[tuple[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    post_body = _find_post_body(soup)

    elements = post_body.find_all(CONTENT_TAGS)

    sections: list[tuple[str, str]] = []
    current_heading: str | None = None
    current_parts: list[str] = []

    def flush():
        if current_heading is not None:
            text = "\n".join(p for p in current_parts if p.strip())
            if text.strip():
                sections.append((current_heading, text))

    for el in elements:
        if el.name == "h3":
            heading_id = el.get("id")
            if heading_id:
                flush()
                current_heading = heading_id.strip()
                current_parts = []
            continue

        if current_heading is None:
            continue  # nothing before the first real heading is kept

        if el.name == "li":
            if el.find_parent("li") is not None:
                continue  # nested list item; its parent <li> already covers it
            text = el.get_text(separator=" ", strip=True)
            if text:
                current_parts.append(text)

        elif el.name == "i":
            if el.find_parent("li") is not None:
                continue  # already captured as part of its enclosing <li>
            text = el.get_text(separator=" ", strip=True)
            if text:
                current_parts.append(text)

        elif el.name == "tr":
            line = _row_text(el)
            if line:
                current_parts.append(line)

    flush()
    return sections
