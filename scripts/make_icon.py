"""Draw the app icon (the letter H on a navy plate) from the bundled Comic Neue font.

    uv run python scripts/make_icon.py

Writes packaging/icon.ico (Windows installer: 16, 32, 48 and 256 px, PNG-compressed) and web/icon.png
(the browser build's favicon). Both are checked in; run this only to change the look.
The font is SIL OFL (see CREDITS.md); the colors are the title card's navy and red.
"""

import io
import os
import struct
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

ROOT = Path(__file__).resolve().parent.parent
FONT = ROOT / "assets" / "fonts" / "ComicNeue-Regular.ttf"
SIZE = 256
NAVY = (28, 32, 64)
RED = (212, 26, 26)


def draw_icon() -> pygame.Surface:
    surface = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
    pygame.draw.rect(surface, NAVY, surface.get_rect(), border_radius=SIZE // 6)
    font = pygame.font.Font(str(FONT), int(SIZE * 0.85))
    font.set_bold(True)
    glyph = font.render("H", True, RED)
    surface.blit(glyph, glyph.get_rect(center=(SIZE // 2, SIZE // 2)))
    return surface


ICO_SIZES = (16, 32, 48, 256)


def ico_bytes(images: dict[int, bytes]) -> bytes:
    """A .ico with one PNG-compressed image per size (256 is stored as 0)."""
    header = struct.pack("<HHH", 0, 1, len(images))
    offset = 6 + 16 * len(images)
    entries = b""
    for size, png in images.items():
        entries += struct.pack(
            "<BBBBHHII", size % 256, size % 256, 0, 0, 1, 32, len(png), offset
        )
        offset += len(png)
    return header + entries + b"".join(images.values())


def png_bytes(surface: pygame.Surface) -> bytes:
    buffer = io.BytesIO()
    pygame.image.save(surface, buffer, "icon.png")
    return buffer.getvalue()


def main() -> None:
    pygame.font.init()
    surface = draw_icon()
    png_path = ROOT / "web" / "icon.png"
    pygame.image.save(surface, str(png_path))
    images = {
        size: png_bytes(
            surface
            if size == SIZE
            else pygame.transform.smoothscale(surface, (size, size))
        )
        for size in ICO_SIZES
    }
    (ROOT / "packaging" / "icon.ico").write_bytes(ico_bytes(images))
    print(f"Wrote {png_path} and packaging/icon.ico")


if __name__ == "__main__":
    main()
