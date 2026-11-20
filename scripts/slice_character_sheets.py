"""Slice the AI-generated walk-cycle sheets into the game's 64x64 frames.

Input: ``scripts/sheets/{vampire,peasant}_sheet.png``, one row of 9 right-facing walk frames on a
flat magenta background. Output: ``assets/images/vampire/{R,L}{1-9}E.png`` and
``assets/images/peasant/{R,L}{1-9}.png`` (L is the mirrored R frame).

Cleanup: magenta is keyed out, the frames are scaled by one factor per character (so the size
stays consistent), alpha is hard (0 or 255), the colors are reduced to a small shared palette,
and every frame sits on the same baseline, at the same horizontal position relative to its
source cell. No dependencies besides pygame.

    uv run python scripts/slice_character_sheets.py
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

ROOT = Path(__file__).resolve().parent.parent
FRAMES = 9
CELL = 64
KEY = (255, 0, 255)
KEY_DISTANCE = (
    120  # max summed channel distance from the key color that counts as background
)
OUTLINE = (24, 14, 28)  # fills keyed-out pixels so the scaler does not bleed magenta
PALETTE_SIZE = 20

# name -> (sheet, output folder, file suffix, character height in px, baseline row (exclusive))
CHARACTERS = {
    "vampire": ("vampire_sheet.png", "vampire", "E", 53, 58),
    "peasant": ("peasant_sheet.png", "peasant", "", 47, 62),
}

Color = tuple[int, int, int]


def is_background(c: pygame.Color) -> bool:
    return abs(c.r - KEY[0]) + abs(c.g - KEY[1]) + abs(c.b - KEY[2]) < KEY_DISTANCE


def cut_frames(sheet: pygame.Surface) -> list[tuple[pygame.Surface, int]]:
    """Each frame cropped to its pixels, with its x offset from the cell center (source px)."""
    w, h = sheet.get_size()
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        for x in range(w):
            c = sheet.get_at((x, y))
            mask.set_at(
                (x, y), (0, 0, 0, 0) if is_background(c) else (c.r, c.g, c.b, 255)
            )
    cell_w = w / FRAMES
    frames = []
    for i in range(FRAMES):
        cell = pygame.Rect(round(i * cell_w), 0, round(cell_w), h)
        box = mask.subsurface(cell).get_bounding_rect()
        box.move_ip(cell.x, 0)
        frames.append((mask.subsurface(box).copy(), box.centerx - cell.centerx))
    return frames


def median_cut(colors: list[Color], n: int) -> list[Color]:
    boxes = [colors]
    while len(boxes) < n:
        boxes.sort(key=len, reverse=True)
        box = boxes.pop(0)
        if len(set(box)) < 2:
            boxes.append(box)
            break
        spans = [max(c[i] for c in box) - min(c[i] for c in box) for i in range(3)]
        ch = spans.index(max(spans))
        box.sort(key=lambda c: c[ch])
        mid = len(box) // 2
        boxes += [box[:mid], box[mid:]]
    return [tuple(sum(c[i] for c in b) // len(b) for i in range(3)) for b in boxes]  # type: ignore[misc]


def nearest(c: Color, palette: list[Color]) -> Color:
    return min(palette, key=lambda p: sum((p[i] - c[i]) ** 2 for i in range(3)))


def build(name: str) -> list[pygame.Surface]:
    sheet_name, _, _, height, baseline = CHARACTERS[name]
    sheet = pygame.image.load(ROOT / "scripts" / "sheets" / sheet_name)
    frames = cut_frames(sheet)
    scale = height / max(f.get_height() for f, _ in frames)
    scaled = []
    for frame, dx in frames:
        flat = frame.copy()
        for y in range(flat.get_height()):
            for x in range(flat.get_width()):
                if flat.get_at((x, y)).a == 0:
                    flat.set_at((x, y), (*OUTLINE, 0))
        size = (
            max(1, round(frame.get_width() * scale)),
            max(1, round(frame.get_height() * scale)),
        )
        scaled.append((pygame.transform.smoothscale(flat, size), round(dx * scale)))
    # one palette per character, made from every opaque pixel of every frame
    pixels = [
        (c.r, c.g, c.b)
        for f, _ in scaled
        for y in range(f.get_height())
        for x in range(f.get_width())
        if (c := f.get_at((x, y))).a >= 128
    ]
    palette = median_cut(pixels, PALETTE_SIZE)
    out = []
    for frame, dx in scaled:
        cell = pygame.Surface((CELL, CELL), pygame.SRCALPHA)
        left = CELL // 2 - frame.get_width() // 2 + dx
        top = baseline - frame.get_height()
        for y in range(frame.get_height()):
            for x in range(frame.get_width()):
                c = frame.get_at((x, y))
                px, py = left + x, top + y
                if c.a >= 128 and 0 <= px < CELL and 0 <= py < CELL:
                    cell.set_at((px, py), (*nearest((c.r, c.g, c.b), palette), 255))
        out.append(cell)
    return out


def main() -> None:
    pygame.init()
    for name, (_, folder, suffix, _, _) in CHARACTERS.items():
        dest = ROOT / "assets" / "images" / folder
        dest.mkdir(parents=True, exist_ok=True)
        for i, frame in enumerate(build(name), start=1):
            pygame.image.save(frame, str(dest / f"R{i}{suffix}.png"))
            pygame.image.save(
                pygame.transform.flip(frame, True, False),
                str(dest / f"L{i}{suffix}.png"),
            )
        print(f"{name}: wrote {2 * FRAMES} frames to {dest}")


if __name__ == "__main__":
    sys.exit(main())
