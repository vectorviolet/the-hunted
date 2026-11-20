"""README and store media from the game's own art: screenshots, preview.gif and the covers.

    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run python scripts/art_gen/shoot.py
    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run --group art python scripts/art_gen/make_media.py [step ...]

Steps (default: all but the devlog ones): ``screenshots``, ``gif``, ``covers``, ``social``, and for
the devlog ``devlog`` and ``cover-sheet``.
Run shoot.py first: the screenshots are made from its frames (the covers and the gif come
from the game directly).
Needs the ``art`` dependency group (Pillow). README and store media stay at full size (screenshots
and preview.gif 1920x1080, itch.io cover 630x500, GitHub social preview 1280x640); only devlog
images are capped at 1280 px wide.
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


SHOTS = (
    ("after_menu", "01_main_menu"),
    ("after_mode", "02_mode_menu"),
    ("after_credits", "03_credits"),
    ("after_level_select", "04_level_select"),
    ("after_level0", "05_round_classic"),
    ("after_level1", "06_round_towers"),
    ("after_level2", "07_round_arena"),
)


def screenshots() -> None:
    out = ROOT / "docs" / "screenshots"
    for src, dst in SHOTS:
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


def tagline(img: Image.Image, text: str, cx: int, y: int, size: int) -> None:
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    small = font("Silkscreen-Regular.ttf", size)
    d.text((cx + size // 8, y + size // 8), text, font=small, fill=INK, anchor="mm")
    d.text((cx, y), text, font=small, fill=GOLD, anchor="mm")


def title_at(img: Image.Image, cx: int, cy: int, size: int) -> None:
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    big = font("Jacquard12-Regular.ttf", size)
    shadow = max(2, size // 12)
    d.text(
        (cx + shadow, cy + shadow), "The Hunted", font=big, fill=CRIMSON, anchor="mm"
    )
    d.text((cx, cy), "The Hunted", font=big, fill=RIM, anchor="mm")


def chase_frame(level: int, vampire_plat: int, peasant_plat: int) -> Image.Image:
    """A 960x540 frame of a round on `level` with the characters close together on two
    platforms and a bullet in the air (the cover's action shot), drawn by the real game."""
    import settings
    from entities import Projectile, level_platforms
    from game import Game

    random.seed(3)
    game = Game()
    game._world.two_players = True
    game._current_level = level
    game._world.platforms = level_platforms(level)
    game._reset_players()
    game._enter_game()
    plats = game._world.platforms
    vampire = game._vampire
    assert vampire is not None
    peasant = game._p2 if vampire is game._p1 else game._p1
    for player, idx, share in (
        (vampire, vampire_plat, 0.25),
        (peasant, peasant_plat, 0.7),
    ):
        plat = plats[idx]
        player.x = plat.x + plat.width * share - 32
        player.y = plat.y - 60
    peasant.hp = int(settings.MAX_HP * 0.7)
    game._world.bullets.clear()
    game._world.bullets.append(
        Projectile(
            int(peasant.x) - 40,
            int(peasant.y) + 36,
            settings.BULLET_RADIUS,
            settings.BULLET_COLOR,
            -1,
        )
    )
    game.draw()
    raw = pygame.image.tobytes(game.window, "RGB")
    return Image.frombytes("RGB", game.window.get_size(), raw)


def action_cover(frame: Image.Image, line: str) -> Image.Image:
    """A 630x500 cover from a 960x540 round frame: its middle 630 px at 1x, with the title on
    a dark veil over the top."""
    img = frame.crop((165, 40, 795, 540)).convert("RGBA")
    assert img.size == (630, 500), img.size
    img.alpha_composite(Image.new("RGBA", (630, 130), (*INK, 170)), (0, 0))
    title_at(img, 315, 52, 12 * 6)
    tagline(img, line, 315, 106, 8 * 2)
    return img.convert("RGB")


CANDIDATES = (
    # name, builder. a: the menu scene (backdrop, ground, both characters); b and c: a crop of a
    # real round on Towers and Arena.
    ("a-menu-scene", lambda: cover((630, 500), 1, 3, 12 * 6, 8 * 2)),
    (
        "b-towers-chase",
        lambda: action_cover(chase_frame(1, 2, 3), "CATCH THEM. OR SHOOT BACK."),
    ),
    (
        "c-arena-duel",
        lambda: action_cover(chase_frame(2, 2, 3), "THE ROLES SWAP EVERY ROUND"),
    ),
)
DEFAULT_COVER = "a-menu-scene"


def covers() -> None:
    """Three itch.io cover candidates (630x500) in docs/store/candidates/; the default is
    copied to docs/store/cover.png."""
    store = ROOT / "docs" / "store"
    (store / "candidates").mkdir(exist_ok=True)
    for name, build in CANDIDATES:
        img = build()
        assert img.size == (630, 500)
        img.save(store / "candidates" / f"{name}.png", optimize=True)
        if name == DEFAULT_COVER:
            img.save(store / "cover.png", optimize=True)


def social_preview() -> None:
    """The GitHub social preview, 1280x640 (GitHub's 2:1): the menu scene with the title."""
    img = cover((1280, 640), 2, 5, 12 * 11, 8 * 3)
    img.save(ROOT / "docs" / "design" / "social-preview.png", optimize=True)


def devlog_comparisons() -> None:
    """The 4:3 game (work/p43_*.png, the 800x600 frames from before the 16:9 change) next to
    the 16:9 one (work/after_*.png), both at 0.7x so the pair fits the devlog's 1280 px."""
    out = ROOT / "docs" / "devlog" / "img"
    scale = 0.7
    for name in ("menu", "level_select", "level0", "level1", "level2"):
        old, new = WORK / f"p43_{name}.png", WORK / f"after_{name}.png"
        missing = [p.name for p in (old, new) if not p.exists()]
        if missing:
            raise SystemExit(
                f"missing {missing} in {WORK}: run scripts/art_gen/shoot.py first (the p43_* "
                "frames are the 800x600 shots from before the 16:9 change, kept by hand)"
            )
        left = Image.open(old).convert("RGB")
        right = Image.open(new).convert("RGB")
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


def cover_sheet() -> None:
    """The three cover candidates side by side for the devlog, 1280 px wide."""
    names = [n for n, _ in CANDIDATES]
    gap, w = 8, 420
    h = round(500 * w / 630)
    sheet = Image.new("RGB", (3 * w + 2 * gap, 24 + h), (24, 20, 28))
    d = ImageDraw.Draw(sheet)
    d.fontmode = "1"
    small = font("Silkscreen-Regular.ttf", 8)
    for i, name in enumerate(names):
        img = Image.open(ROOT / "docs" / "store" / "candidates" / f"{name}.png")
        x = i * (w + gap)
        d.text((x + 4, 8), name.upper(), font=small, fill=GOLD)
        sheet.paste(img.resize((w, h), Image.Resampling.BOX), (x, 24))
    sheet.save(
        ROOT / "docs" / "devlog" / "img" / "22-cover-candidates.png", optimize=True
    )


STEPS = {
    "screenshots": screenshots,
    "gif": preview_gif,
    "covers": covers,
    "social": social_preview,
    "devlog": devlog_comparisons,
    "cover-sheet": cover_sheet,
}


def main(steps: list[str]) -> None:
    unknown = [n for n in steps if n not in STEPS]
    if unknown:
        raise SystemExit(f"unknown step {unknown}; choose from {list(STEPS)}")
    pygame.init()
    pygame.display.set_mode((1, 1))
    for name in steps or [n for n in STEPS if n not in ("devlog", "cover-sheet")]:
        STEPS[name]()
    print("ok")


if __name__ == "__main__":
    main(sys.argv[1:])
