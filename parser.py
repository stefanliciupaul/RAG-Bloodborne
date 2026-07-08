"""
Parser for the bloodborne-wiki.com 
"""

from bs4 import BeautifulSoup, Tag, NavigableString, Comment

POST_BODY_SELECTORS = [
    ("div", {"class": "post-body"}),
    ("div", {"class": "entry-content"}),
    ("article", {}),
]

HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
SKIP_TAGS = {"script", "style"}


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
    raise ValueError(
    )


def _direct_rows(table: Tag) -> list[Tag]:
    return [tr for tr in table.find_all("tr") if tr.find_parent("table") is table]


def _direct_cells(row: Tag) -> list[Tag]:
    return [c for c in row.find_all(["td", "th"]) if c.find_parent("tr") is row]


class _SectionState:

    def __init__(self):
        self.sections: list[tuple[str, str]] = []
        self.current_heading = "Introduction"
        self.buffer: list[str] = []

    def flush(self):
        text = "\n\n".join(p for p in self.buffer if p.strip()).strip()
        if text:
            self.sections.append((self.current_heading, text))
        self.buffer.clear()

    def add_heading(self, heading: str):
        if heading:
            self.flush()
            self.current_heading = heading

    def add_text(self, text: str):
        text = " ".join(text.split())  # collapse internal whitespace
        if text:
            self.buffer.append(text)


def _row_contains_heading(row: Tag) -> bool:
    return row.find(lambda t: isinstance(t, Tag) and t.name in HEADING_TAGS) is not None


def _process_table(table: Tag, state: "_SectionState") -> None:
    for row in _direct_rows(table):
        if _row_contains_heading(row):
            _walk(row, state)
            continue

        cells = _direct_cells(row)
        if len(cells) == 1:
            _walk(cells[0], state)
        elif len(cells) > 1:
            line = " | ".join(
                c.get_text(separator=" ", strip=True) for c in cells
                if c.get_text(strip=True)
            )
            if line:
                state.buffer.append(line)


def _walk(node: Tag, state: "_SectionState") -> None:
    for child in node.children:
        if isinstance(child, Tag):
            if child.name in HEADING_TAGS:
                state.add_heading(child.get_text(strip=True))
            elif child.name == "table":
                _process_table(child, state)
            elif child.name in SKIP_TAGS:
                continue
            else:
                _walk(child, state)
        elif isinstance(child, Comment):
            continue
        elif isinstance(child, NavigableString):
            state.add_text(str(child))


def extract_sections(html: str) -> list[tuple[str, str]]:
    soup = BeautifulSoup(html, "html.parser")
    post_body = _find_post_body(soup)

    state = _SectionState()
    _walk(post_body, state)
    state.flush()
    return state.sections
