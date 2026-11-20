"""README and store media from the game's own art: screenshots, preview.gif and the covers.

    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run python scripts/art_gen/shoot.py
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run --group art python scripts/art_gen/make_media.py

Needs the ``art`` dependency group (Pillow). README and store media stay at full 1920x1080
(screenshots, preview.gif) and the store sizes (cover 2752x1536, itch.io cover 630x500); only
devlog images are capped at 1280 px wide.
"""

from __future__ import annotations

import os
import random
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "src" / "pygamine"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pygame  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

import palette  # noqa: E402

WORK = Path(__file__).resolve().parent / "work"
IMAGES = ROOT / "assets" / "images"
FONTS = ROOT / "assets" / "fonts"
RIM = (255, 244, 214)
CRIMSON = (159, 27, 41)
BONE = (217, 215, 220)
GOLD = (243, 190, 81)
INK = (20, 14, 20)  # #140e14, the palette ink
FULL = (1920, 1080)


def letterbox(frame: Image.Image) -> Image.Image:
    """The 960x540 game frame the way the real window shows it fullscreen on a 1920x1080
    screen: an exact 2x, nearest-neighbor."""
    assert frame.size == (960, 540), frame.size
    return frame.convert("RGB").resize(FULL, Image.Resampling.NEAREST)


def screenshots() -> None:
    out = ROOT / "docs" / "screenshots"
    for src, dst in (
        ("after_menu", "01_main_menu"),
        ("after_level_select", "02_level_select"),
        ("after_level1", "03_round_in_progress"),
    ):
        letterbox(Image.open(WORK / f"{src}.png")).save(
            out / f"{dst}.png", optimize=True
        )


def preview_gif(seconds: float = 6.0, fps: int = 30) -> None:
    """A short AI-versus-AI round on the Towers level, 1920x1080."""
    import settings
    from entities import level_platforms
    from game import Game
    from input_handler import AIInputHandler

    random.seed(7)
    game = Game()
    game._current_level = 1
    game._world.platforms = level_platforms(1)
    game._reset_players()
    game._enter_game()
    for me, other in ((game._p1, game._p2), (game._p2, game._p1)):
        me._input = AIInputHandler()
        me._input.bind(me, other)
    game._world.two_players = True

    frames: list[Image.Image] = []
    pal = Image.new("P", (1, 1))
    flat = [c for rgb in palette.master() for c in rgb]
    pal.putpalette(flat + [0] * (768 - len(flat)))
    step = 60 // fps
    for i in range(int(seconds * 60)):
        game.update()
        game.draw()
        if i % step == 0:
            raw = pygame.image.tobytes(game.window, "RGB")
            frame = Image.frombytes("RGB", game.window.get_size(), raw)
            frames.append(
                letterbox(frame).quantize(palette=pal, dither=Image.Dither.NONE)
            )
    assert game._current_level == 1 and settings.LEVELS[1]["name"] == "Towers"
    frames[0].save(
        ROOT / "docs" / "preview.gif",
        save_all=True,
        append_images=frames[1:],
        duration=1000 // fps,
        loop=0,
        optimize=True,
    )


# ---------------------------------------------------------------- covers


def font(name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(
        str(FONTS / name), size, layout_engine=ImageFont.Layout.BASIC
    )


def tiled(sheet: Image.Image, width: int, scale: int) -> Image.Image:
    """A ground strip `width` px wide from a cap | middle | cap sheet (art px x `scale`)."""
    sheet = sheet.resize(
        (sheet.width * scale // 2, sheet.height * scale // 2), Image.Resampling.NEAREST
    )
    cap, mid = 16 * scale // 2, 32 * scale // 2
    strip = Image.new("RGBA", (width, sheet.height))
    strip.paste(sheet.crop((0, 0, cap, sheet.height)), (0, 0))
    x = cap
    while x < width - cap:
        strip.paste(sheet.crop((cap, 0, cap + mid, sheet.height)), (x, 0))
        x += mid
    strip.paste(
        sheet.crop((cap + mid, 0, 2 * cap + mid, sheet.height)), (width - cap, 0)
    )
    return strip


def cover(
    size: tuple[int, int], bg_scale: int, char_scale: int, title: int, sub: int
) -> Image.Image:
    """The menu backdrop, ground and both characters, with the title."""
    w, h = size
    bg = Image.open(IMAGES / "background" / "menu.png").convert("RGB")
    bg = bg.resize(
        (bg.width * bg_scale, bg.height * bg_scale), Image.Resampling.NEAREST
    )
    left, top = (bg.width - w) // 2, (bg.height - h) // 2
    img = bg.crop((left, top, left + w, top + h)).convert("RGBA")
    ground = tiled(
        Image.open(IMAGES / "ground" / "towers.png").convert("RGBA"), w, bg_scale
    )
    ground_y = h - ground.height
    img.alpha_composite(ground, (0, ground_y))
    for path, x in (
        (IMAGES / "vampire" / "R1E.png", int(w * 0.14)),
        (IMAGES / "peasant" / "L1.png", int(w * 0.66)),
    ):
        sprite = Image.open(path).convert("RGBA")
        sprite = sprite.resize(
            (64 * char_scale, 64 * char_scale), Image.Resampling.NEAREST
        )
        # The feet are about 4 sprite px above the frame's bottom edge.
        img.alpha_composite(sprite, (x, ground_y - sprite.height + 4 * char_scale))
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    big = font("Jacquard12-Regular.ttf", title)
    shadow = max(2, title // 12)
    cx, cy = w // 2, int(h * 0.27)
    d.text(
        (cx + shadow, cy + shadow), "The Hunted", font=big, fill=CRIMSON, anchor="mm"
    )
    d.text((cx, cy), "The Hunted", font=big, fill=RIM, anchor="mm")
    small = font("Silkscreen-Regular.ttf", sub)
    line = "A VAMPIRE CHASE FOR ONE OR TWO"
    sy = cy + title // 2 + sub
    d.text((cx + sub // 8, sy + sub // 8), line, font=small, fill=INK, anchor="mm")
    d.text((cx, sy), line, font=small, fill=GOLD, anchor="mm")
    return img.convert("RGB")


def covers() -> None:
    store = ROOT / "docs" / "store"
    cover((2752, 1536), 4, 8, 12 * 24, 8 * 7).save(store / "cover.png", optimize=True)
    cover((630, 500), 1, 3, 12 * 6, 8 * 2).save(
        store / "cover_itchio.png", optimize=True
    )


def devlog_comparisons() -> None:
    """The 4:3 game (work/p43_*.png, the 800x600 frames from before the 16:9 change) next to
    the 16:9 one (work/after_*.png), both at 0.7x so the pair fits the devlog's 1280 px."""
    out = ROOT / "docs" / "devlog" / "img"
    scale = 0.7
    for name in ("menu", "level_select", "level0", "level1", "level2"):
        old = WORK / f"p43_{name}.png"
        if not old.exists():
            continue
        left = Image.open(old).convert("RGB")
        right = Image.open(WORK / f"after_{name}.png").convert("RGB")
        left = left.resize((round(w * scale) for w in left.size), Image.Resampling.BOX)
        right = right.resize(
            (round(w * scale) for w in right.size), Image.Resampling.BOX
        )
        height = max(left.height, right.height)
        sheet = Image.new(
            "RGB", (left.width + 8 + right.width, 26 + height), (24, 20, 28)
        )
        d = ImageDraw.Draw(sheet)
        d.fontmode = "1"
        small = font("Silkscreen-Regular.ttf", 8)
        d.text((6, 8), "4:3 (800X600)", font=small, fill=BONE)
        d.text((left.width + 14, 8), "16:9 (960X540)", font=small, fill=GOLD)
        sheet.paste(left, (0, 26))
        sheet.paste(right, (left.width + 8, 26))
        sheet.save(out / f"19-169-{name.replace('_', '-')}.png", optimize=True)


def main() -> None:
    pygame.init()
    pygame.display.set_mode((1, 1))
    devlog_comparisons()
    screenshots()
    covers()
    preview_gif()
    print("ok")


if __name__ == "__main__":
    main()
