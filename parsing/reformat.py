"""
Reformats the Weak Points table into one natural-language
sentence per body part.
"""

_HEADER_PREFIX = "Body Part"


def _parse_header(line: str) -> list[str]:
    return [c.strip() for c in line.split("|")]


def _parse_row(line: str, n_cols: int) -> list[str] | None:
    cells = [c.strip() for c in line.split("|")]
    if len(cells) != n_cols:
        return None
    return cells


def _row_to_sentence(headers: list[str], cells: list[str]) -> str:
    field_map = dict(zip(headers, cells))
    body_part = field_map.get("Body Part", "Unknown part")
    total_hp = field_map.get("Total HP")
    part_hp = field_map.get("Part HP")
    hp_pct = field_map.get("HP [%]")
    dmg_before = field_map.get("Damage X")
    dmg_after = field_map.get("Damage X after breaking")

    parts = [f"{body_part}:"]
    if part_hp and hp_pct:
        parts.append(f"needs {part_hp} damage ({hp_pct} of total boss HP) to break,")
    if total_hp:
        parts.append(f"boss total HP {total_hp},")
    if dmg_before:
        parts.append(f"takes {dmg_before}x damage normally")
    if dmg_after:
        parts.append(f"and {dmg_after}x damage after being broken.")

    return " ".join(parts)


def reformat_weak_points(text: str) -> str:
    """
    Finds the "Body Part | ..." header line and converts every following
    pipe-delimited data row into a sentence.
    """
    lines = text.split("\n")

    header_idx = next(
        (i for i, line in enumerate(lines) if line.strip().startswith(_HEADER_PREFIX)),
        None,
    )
    if header_idx is None:
        return text  # doesn't match the expected format -- leave as-is

    headers = _parse_header(lines[header_idx])
    n_cols = len(headers)

    sentences = []
    notes_idx = None
    for i in range(header_idx + 1, len(lines)):
        line = lines[i]
        if line.strip().startswith("Notes"):
            notes_idx = i
            break
        cells = _parse_row(line, n_cols)
        if cells is not None:
            sentences.append(_row_to_sentence(headers, cells))
        # else: silently skip (stray header continuation, blank lines, etc.)

    before = lines[:header_idx]
    after = lines[notes_idx:] if notes_idx is not None else []
    return "\n".join(before + sentences + after).strip()
