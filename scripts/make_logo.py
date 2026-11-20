"""Render the README wordmark: "The Hunted" in the title font, as pixel art.

    uv run python scripts/make_logo.py

Writes docs/logo.png and the devlog's smaller copy (checked in; run this only to change the logo). The text is drawn
with Jacquard 12 (settings.TITLE_FONT) at size 24 (the smallest size where it is legible)
without anti-aliasing. A one-pixel INK outline and a CRIMSON drop shadow (the menu
title's colors) go on that native grid, then the whole image is scaled up with
nearest-neighbor by a whole factor, so every logo pixel is a crisp block.
The background is transparent. See docs/devlog/2026-11-21-readme-logo.md.
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import settings  # noqa: E402

TEXT = "The Hunted"
FONT_SIZE = (
    24  # Jacquard 12 is only legible from 24 px up; 24 is a whole multiple of its grid
)
PAD = 3  # transparent border in native pixels (room for outline and shadow)
SHADOW_OFFSET = (1, 2)
# (file, whole scale factor): the README logo is about 1700 px wide, the devlog copy stays
# under the 1280 px cap for devlog images.
OUTPUTS = (
    (ROOT / "docs" / "logo.png", 15),
    (ROOT / "docs" / "devlog" / "img" / "readme-logo.png", 10),
)


def tinted(mask: pygame.Mask, color: tuple[int, int, int]) -> pygame.Surface:
    """The mask as a surface of one solid color on a transparent background."""
    return mask.to_surface(setcolor=color, unsetcolor=(0, 0, 0, 0))


def render_native() -> pygame.Surface:
    """The wordmark at one pixel per font pixel: shadow, outline, then fill."""
    font = pygame.font.Font(str(ROOT / settings.TITLE_FONT), FONT_SIZE)
    text = font.render(TEXT, False, (255, 255, 255))
    fill = pygame.mask.from_surface(text)
    # The outline is the fill grown by one pixel in all 8 directions.
    outline = pygame.Mask(fill.get_size())
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            outline.draw(fill, (dx, dy))
    w, h = fill.get_size()
    canvas = pygame.Surface((w + 2 * PAD, h + 2 * PAD), pygame.SRCALPHA)
    shadow_at = (PAD + SHADOW_OFFSET[0], PAD + SHADOW_OFFSET[1])
    canvas.blit(tinted(outline, settings.CRIMSON), shadow_at)
    canvas.blit(tinted(outline, settings.INK), (PAD, PAD))
    canvas.blit(tinted(fill, settings.RIM), (PAD, PAD))
    return canvas


def main() -> None:
    pygame.init()
    native = render_native()
    for path, scale in OUTPUTS:
        size = (native.get_width() * scale, native.get_height() * scale)
        pygame.image.save(pygame.transform.scale(native, size), str(path))
        print(f"wrote {path.relative_to(ROOT)} ({size[0]}x{size[1]}, {scale}x scale)")


if __name__ == "__main__":
    main()
