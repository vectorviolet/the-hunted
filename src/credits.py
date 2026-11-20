"""The credits page's text, built from assets/SOURCES.yaml (the same data CREDITS.md's asset
table is generated from) so the two can't disagree about who made what.

Sections come in a fixed order: the game, music, sounds, art, fonts, engine. A pack lands in a
section by where its files live: `fonts/` is fonts, `images/` is art, and `sounds/` is music when
the pack's `used_for` mentions music, sounds otherwise. Files with source `own` are credited to
the developer; `unknown` ones are credited to no one.
"""

from typing import Any

import yaml

SOURCES_FILE = "assets/SOURCES.yaml"
DEVELOPER = "VectorViolet"
ENGINE_LINES = ("pygame-ce (LGPL 2.1)", "pygamine (MIT)")
OWN = "own"
UNKNOWN = "unknown"

CreditSection = tuple[str, list[str]]


def _license(slug: str) -> str:
    """A license id as shown on the page: "CC0-1.0" -> "CC0 1.0", "OFL-1.1" -> "OFL 1.1"."""
    return slug.replace("-", " ")


def _pack_line(pack: dict[str, Any]) -> str:
    return f"{pack['name']} - {pack['author']} ({_license(pack['license'])})"


def _own_line(entry: dict[str, Any]) -> str:
    tool = entry.get("generated_with")
    return f"AI-generated with {tool}" if tool else f"Made by {DEVELOPER}"


def _section_of(rel: str, pack: dict[str, Any] | None) -> str | None:
    """The credits section a file belongs to (None for a file in an unexpected folder)."""
    folder = rel.split("/", 1)[0]
    if folder == "fonts":
        return "FONTS"
    if folder == "images":
        return "ART"
    if folder == "sounds":
        used_for = pack["used_for"] if pack else ""
        return "MUSIC" if "music" in used_for else "SOUNDS"
    return None


def credit_sections(data: dict[str, Any]) -> list[CreditSection]:
    """The credits as (heading, lines) pairs, from parsed SOURCES.yaml data."""
    packs: dict[str, Any] = data["packs"]
    lines: dict[str, list[str]] = {
        name: [] for name in ("MUSIC", "SOUNDS", "ART", "FONTS")
    }
    for rel, entry in sorted(data["files"].items()):
        source = entry["source"]
        if source == UNKNOWN:
            continue
        pack = None if source == OWN else packs[source]
        section = _section_of(rel, pack)
        line = _own_line(entry) if pack is None else _pack_line(pack)
        if section is not None and line not in lines[section]:
            lines[section].append(line)
    sections: list[CreditSection] = [("GAME", [DEVELOPER])]
    sections += [(name, found) for name, found in lines.items() if found]
    sections.append(("ENGINE", list(ENGINE_LINES)))
    return sections


def load_credit_sections(path: str = SOURCES_FILE) -> list[CreditSection]:
    """The credits from the SOURCES.yaml file at `path` (relative to the working directory,
    like the rest of the assets)."""
    with open(path, encoding="utf-8") as file:
        return credit_sections(yaml.safe_load(file))
