"""Build the app icon files from one of the AI-generated candidates in scripts/icons/.

    uv run python scripts/make_icon.py          # default candidate (DEFAULT)
    uv run python scripts/make_icon.py b        # another one: cand_b.png
    uv run python scripts/make_icon.py --preview  # docs/devlog/img/icon-candidates.png

Writes packaging/icon.ico (Windows installer and exe: 16, 32, 48 and 256 px,
PNG-compressed), web/icon.png (256 px, the browser build's favicon) and
assets/images/icon/icon_64.png (the window icon). All three are checked in; run this only
to change the icon. The candidates (1024 px) were made with OpenAI Codex image generation,
see docs/devlog/2026-11-20-browser-build-and-installer.md.
"""

import io
import os
import struct
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

ROOT = Path(__file__).resolve().parent.parent
CANDIDATES = ROOT / "scripts" / "icons"
DEFAULT = "a"
ICO_SIZES = (16, 32, 48, 256)
WINDOW_ICON_SIZE = 64


def load(name: str) -> pygame.Surface:
    return pygame.image.load(str(CANDIDATES / f"cand_{name}.png"))


def scaled(source: pygame.Surface, size: int) -> pygame.Surface:
    return pygame.transform.smoothscale(source, (size, size))


def png_bytes(surface: pygame.Surface) -> bytes:
    buffer = io.BytesIO()
    pygame.image.save(surface, buffer, "icon.png")
    return buffer.getvalue()


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


def write_icons(name: str) -> None:
    source = load(name)
    images = {size: png_bytes(scaled(source, size)) for size in ICO_SIZES}
    (ROOT / "packaging" / "icon.ico").write_bytes(ico_bytes(images))
    (ROOT / "web" / "icon.png").write_bytes(images[256])
    window = ROOT / "assets" / "images" / "icon" / "icon_64.png"
    window.parent.mkdir(parents=True, exist_ok=True)
    window.write_bytes(png_bytes(scaled(source, WINDOW_ICON_SIZE)))
    print(f"Wrote the icons from candidate {name}")


def write_preview() -> None:
    """Every candidate at 256, 48, 32 and 16 px (the small ones enlarged 2x by
    nearest-neighbor, so the pixels they really have are visible)."""
    names = sorted(p.stem.removeprefix("cand_") for p in CANDIDATES.glob("cand_*.png"))
    cell, pad = 256, 16
    sheet = pygame.Surface((len(names) * (cell + pad) + pad, cell + 2 * pad + 64 * 2))
    sheet.fill((40, 40, 48))
    font = pygame.font.Font(
        str(ROOT / "assets" / "fonts" / "Silkscreen-Regular.ttf"), 24
    )
    for i, name in enumerate(names):
        x = pad + i * (cell + pad)
        source = load(name)
        sheet.blit(scaled(source, cell), (x, pad))
        sheet.blit(font.render(name.upper(), True, (255, 255, 255)), (x + 6, pad + 4))
        for j, size in enumerate((48, 32, 16)):
            small = scaled(source, size)
            sheet.blit(
                pygame.transform.scale(small, (size * 2, size * 2)),
                (x + j * 90, cell + 2 * pad),
            )
    out = ROOT / "docs" / "devlog" / "img" / "icon-candidates.png"
    pygame.image.save(sheet, str(out))
    print(f"Wrote {out}")


def main(argv: list[str]) -> None:
    pygame.font.init()
    if argv == ["--preview"]:
        write_preview()
    else:
        write_icons(argv[0] if argv else DEFAULT)


if __name__ == "__main__":
    main(sys.argv[1:])
