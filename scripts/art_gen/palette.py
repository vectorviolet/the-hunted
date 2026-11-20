"""The shared palette of the Hunted art style (see docs/design/art-style.md).

``CORE`` is read off the new characters and icon A (the anchors). ``SCENERY`` adds the lighter,
duller ramps that backgrounds, platforms and UI need; every ramp keeps the sprites' hue family
(violet-black darks, bone whites, crimson, straw gold, moss green, brown) so nothing looks
pasted in. Every generated asset is reduced to exactly these colors, with hard edges.
"""

from __future__ import annotations

# Pulled from assets/images/vampire, assets/images/peasant and the icon.
CORE: dict[str, list[str]] = {
    "ink": [
        "#0c080a",
        "#140e14",
        "#1c191c",
        "#240924",
        "#28242b",
        "#350d2a",
        "#301b33",
    ],
    "rim": ["#fff4d6"],
    "bone": ["#d9d7dc", "#dbcdcb", "#beaead", "#9a8b8a"],
    "plum": ["#6c4d6e", "#791267"],
    "crimson": ["#5e111f", "#9f1b29", "#ff0000"],
    "brown": ["#4d2110", "#642e11", "#7f4a22", "#a76232", "#cf8944"],
    "skin": ["#f4a668", "#f6d29c"],
    "gold": ["#b07f40", "#e49b49", "#f3be51"],
    "moss": ["#4c521a"],
}

# Lighter, duller ramps for scenery (dark to light).
SCENERY: dict[str, list[str]] = {
    "dusk": [
        "#5b4a78",
        "#6e5d8c",
        "#8272a0",
        "#9686b2",
        "#aa9cc2",
        "#bdb2d0",
        "#cfc7dc",
        "#e0dae8",
    ],
    "slate": ["#4f5870", "#65708a", "#7b87a1", "#929db6", "#aab4c9"],
    "rose": ["#8a5a70", "#a8708a", "#c48a9c", "#d9a5ac", "#ecc3b8", "#f4dcc4"],
    "stone": ["#6a6470", "#837d8a", "#9d97a4", "#b7b1bd", "#d0cbd4"],
    "sand": ["#a08c78", "#b9a58c", "#d2c1a4", "#e6d8bf"],
    "grass": ["#6a7a3a", "#8a9a52", "#a8b46c"],
    "torch": ["#d9692a", "#f6e08a"],
    "banner": ["#b83a45", "#d86a70"],
}


def _hex(h: str) -> tuple[int, int, int]:
    return int(h[1:3], 16), int(h[3:5], 16), int(h[5:7], 16)


def core() -> list[tuple[int, int, int]]:
    return [_hex(h) for ramp in CORE.values() for h in ramp]


def master() -> list[tuple[int, int, int]]:
    """Every color of the style, in a stable order, without duplicates."""
    seen: dict[tuple[int, int, int], None] = {}
    for ramps in (CORE, SCENERY):
        for ramp in ramps.values():
            for h in ramp:
                seen[_hex(h)] = None
    return list(seen)
