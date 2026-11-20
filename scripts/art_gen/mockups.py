"""Composite the art-style mockups: today (current main) vs proposed, plus candidate sheets.

    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run python scripts/art_gen/shoot_today.py
    python scripts/art_gen/mockups.py

Needs Pillow and numpy. Reads assets/images/style/*, the character frames in
assets/images/{vampire,peasant}/, assets/fonts/ and scripts/art_gen/work/today_*.png; writes
docs/devlog/img/19-*.png (all at most 1280 px wide, the devlog rule).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
import palette  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
STYLE = ROOT / "assets" / "images" / "style"
OUT = ROOT / "docs" / "devlog" / "img"
TODAY = Path(__file__).resolve().parent / "work"
FONTS = ROOT / "assets" / "fonts"

W, H = 800, 600
GROUND_Y = 550
LEVELS = {
    "classic": [((0, 400), 300, 50), ((500, 400), 300, 50), ((250, 250), 300, 50)],
    "towers": [
        ((0, 430), 220, 30),
        ((580, 430), 220, 30),
        ((150, 300), 220, 30),
        ((430, 300), 220, 30),
        ((310, 170), 180, 30),
    ],
    "arena": [
        ((50, 480), 160, 20),
        ((590, 480), 160, 20),
        ((200, 370), 180, 20),
        ((420, 370), 180, 20),
        ((0, 260), 200, 20),
        ((600, 260), 200, 20),
        ((300, 190), 200, 20),
    ],
}
# The owner's picks; the defaults marked in docs/design/art-style.md.
DEFAULT = {
    "menu": "a",
    "classic": "a",
    "towers": "a",
    "arena": "a",
    "ui": "a",
}

INK = (28, 11, 24)
RIM = (255, 244, 214)
BONE = (217, 215, 220)
CRIMSON = (159, 27, 41)
PLUM = (108, 77, 110)
MOSS = (138, 154, 82)
GOLD = (243, 190, 81)


def load(name: str) -> Image.Image:
    return Image.open(STYLE / f"{name}.png").convert("RGBA")


def font(kind: str, size: int) -> ImageFont.FreeTypeFont:
    files = {
        "jacquard": "Jacquard12-Regular.ttf",
        "silk": "Silkscreen-Regular.ttf",
        "press": "PressStart2P-Regular.ttf",
    }
    return ImageFont.truetype(
        str(FONTS / files[kind]), size, layout_engine=ImageFont.Layout.BASIC
    )


def text(
    img: Image.Image,
    xy: tuple[int, int],
    s: str,
    f: ImageFont.FreeTypeFont,
    color=BONE,
    anchor: str = "la",
    shadow: tuple[int, int, int] | None = INK,
    shadow_px: int = 2,
) -> None:
    d = ImageDraw.Draw(img)
    d.fontmode = "1"  # no anti-aliasing: hard pixel edges
    if shadow is not None:
        d.text(
            (xy[0] + shadow_px, xy[1] + shadow_px),
            s,
            font=f,
            fill=shadow,
            anchor=anchor,
        )
    d.text(xy, s, font=f, fill=color, anchor=anchor)


def paste(dst: Image.Image, src: Image.Image, xy: tuple[int, int]) -> None:
    dst.alpha_composite(src, (xy[0], xy[1])) if xy[0] >= 0 and xy[
        1
    ] >= 0 else dst.paste(src, xy, src)


def nine_slice(src: Image.Image, border: int, size: tuple[int, int]) -> Image.Image:
    w, h = src.size
    tw, th = size
    out = Image.new("RGBA", size)
    xs = [
        (0, border, 0, border),
        (border, w - border, border, tw - border),
        (w - border, w, tw - border, tw),
    ]
    ys = [
        (0, border, 0, border),
        (border, h - border, border, th - border),
        (h - border, h, th - border, th),
    ]
    for sx0, sx1, dx0, dx1 in xs:
        for sy0, sy1, dy0, dy1 in ys:
            piece = src.crop((sx0, sy0, sx1, sy1)).resize(
                (dx1 - dx0, dy1 - dy0), Image.Resampling.NEAREST
            )
            out.paste(piece, (dx0, dy0))
    return out


def three_slice(sheet: Image.Image, width: int) -> Image.Image:
    """Platform of ``width`` px from a cap | middle | cap sheet (caps are 16 px, middle 32 px)."""
    cap, mid = 16, 32
    h = sheet.height
    out = Image.new("RGBA", (width, h))
    out.paste(sheet.crop((0, 0, cap, h)), (0, 0))
    x = cap
    while x < width - cap:
        piece = sheet.crop((cap, 0, cap + mid, h))
        out.paste(piece.crop((0, 0, min(mid, width - cap - x), h)), (x, 0))
        x += mid
    out.paste(sheet.crop((cap + mid, 0, cap + mid + cap, h)), (width - cap, 0))
    return out


def character(role: str, facing_left: bool = False, frame: int = 1) -> Image.Image:
    folder = "vampire" if role == "vampire" else "peasant"
    stem = f"{'L' if facing_left else 'R'}{frame}{'E' if role == 'vampire' else ''}"
    return Image.open(ROOT / "assets" / "images" / folder / f"{stem}.png").convert(
        "RGBA"
    )


def draw_level(
    level: str, variant: str, *, hud: bool = True, chars: bool = True
) -> Image.Image:
    img = load(f"bg_{level}_{variant}").copy()
    ui = DEFAULT["ui"]
    ground = load(f"ground_{level}")
    img.alpha_composite(three_slice(ground, W), (0, GROUND_Y))
    plat = load(f"platform_{level}")
    for (x, y), w, _h in LEVELS[level]:
        img.alpha_composite(three_slice(plat, w), (x, y))
    if chars:
        plats = LEVELS[level]
        v_pos = (plats[0][0][0] + 90, plats[0][0][1])
        p_pos = (plats[1][0][0] + plats[1][1] - 150, plats[1][0][1])
        for role, (px, py), left in (
            ("vampire", v_pos, False),
            ("peasant", p_pos, True),
        ):
            img.alpha_composite(character(role, left), (px, py - 60))
            tag = "VAMPIRE" if role == "vampire" else "PEASANT"
            col = (216, 106, 112) if role == "vampire" else (168, 180, 108)
            tw = 7 * 14 + 10
            box = (px + 32 - tw // 2, py - 60 - 52, px + 32 + tw // 2, py - 60 - 30)
            draw_box(img, box)
            text(
                img,
                (px + 32, py - 60 - 41),
                tag,
                font("silk", 16),
                col,
                "mm",
                shadow=None,
            )
            bar = (px + 6, py - 60 - 14, px + 58, py - 60 - 8)
            draw_bar(img, bar, 0.8 if role == "vampire" else 0.55)
    if hud:
        draw_hud(img, level, ui)
    return img


def draw_box(img: Image.Image, box: tuple[int, int, int, int], edge=PLUM) -> None:
    d = ImageDraw.Draw(img)
    d.rectangle(box, fill=INK)
    d.rectangle(box, outline=edge, width=2)


def draw_bar(img: Image.Image, box: tuple[int, int, int, int], pct: float) -> None:
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = box
    d.rectangle(box, fill=INK)
    fill_col = MOSS if pct > 0.5 else GOLD if pct > 0.25 else (216, 106, 112)
    d.rectangle(
        (x0 + 1, y0 + 1, x0 + 1 + int((x1 - x0 - 2) * pct), y1 - 1), fill=fill_col
    )
    d.rectangle(box, outline=RIM, width=1)


def draw_hud(img: Image.Image, level: str, ui: str) -> None:
    f = font("silk", 16)
    for xy, label, edge in (
        ((0, 0), "P1  0", (79, 88, 112)),
        (((W - 100), 0), "P2  0", CRIMSON),
    ):
        box = (xy[0], 0, xy[0] + 100, 34)
        draw_box(img, box, edge)
        text(img, (box[0] + 50, 17), label, f, BONE, "mm", shadow=None)
    text(img, (W // 2, 18), level.upper(), font("silk", 16), RIM, "mm")


def side_by_side(
    today: Path | None, proposed: Image.Image, title: str, name: str
) -> None:
    pw = 636
    ph = pw * 3 // 4
    sheet = Image.new("RGB", (pw * 2 + 8, ph + 26), (24, 20, 28))
    d = ImageDraw.Draw(sheet)
    d.fontmode = "1"
    small = font("silk", 8)
    d.text((6, 8), f"TODAY - {title}".upper(), font=small, fill=BONE)
    d.text((pw + 14, 8), f"PROPOSED - {title}".upper(), font=small, fill=GOLD)
    if today is not None and today.exists():
        sheet.paste(
            Image.open(today).convert("RGB").resize((pw, ph), Image.Resampling.NEAREST),
            (0, 26),
        )
    else:
        d.rectangle((0, 26, pw, 26 + ph), fill=(40, 34, 46))
        d.text(
            (pw // 2, 26 + ph // 2),
            "NOT IN THE GAME YET",
            font=small,
            fill=PLUM,
            anchor="mm",
        )
    sheet.paste(
        proposed.convert("RGB").resize((pw, ph), Image.Resampling.NEAREST), (pw + 8, 26)
    )
    OUT.mkdir(parents=True, exist_ok=True)
    sheet.save(OUT / f"19-{name}.png")


# ------------------------------------------------------------------ screens


def menu_chars(img: Image.Image) -> None:
    img.alpha_composite(three_slice(load("ground_towers"), W), (0, GROUND_Y))
    img.alpha_composite(character("vampire"), (120, GROUND_Y - 60))
    img.alpha_composite(character("peasant", True), (610, GROUND_Y - 60))


def button(img: Image.Image, label: str, y: int, state: str = "normal") -> None:
    b = load(f"ui_button_{DEFAULT['ui']}_{state}")
    x = (W - b.width) // 2
    img.alpha_composite(b, (x, y))
    off = 2 if state == "pressed" else 0
    text(
        img, (W // 2, y + b.height // 2 - 2 + off), label, font("silk", 24), BONE, "mm"
    )


def screen_menu(labels: tuple[str, str, str], hover: int = 0) -> Image.Image:
    img = load(f"bg_menu_{DEFAULT['menu']}").copy()
    menu_chars(img)
    text(
        img,
        (W // 2, 105),
        "The Hunted",
        font("jacquard", 96),
        RIM,
        "mm",
        shadow=CRIMSON,
        shadow_px=4,
    )
    for i, label in enumerate(labels):
        button(img, label, 215 + i * 84, "hover" if i == hover else "normal")
    return img


def screen_credits() -> Image.Image:
    img = load(f"bg_menu_{DEFAULT['menu']}").copy()
    menu_chars(img)
    panel = nine_slice(load(f"ui_panel_{DEFAULT['ui']}"), 20, (540, 430))
    img.alpha_composite(panel, ((W - 540) // 2, 40))
    text(img, (W // 2, 90), "Credits", font("jacquard", 60), RIM, "mm", shadow=CRIMSON)
    lines = [
        "Art  AI-generated with OpenAI Codex",
        "Music  HydroGene (CC0)",
        "Sounds  Kenney (CC0)",
        "Fonts  Jacquard 12, Silkscreen (OFL)",
        "Engine  pygame-ce and pygamine",
    ]
    for i, line in enumerate(lines):
        text(img, (W // 2, 160 + i * 38), line, font("silk", 16), BONE, "mm")
    button(img, "BACK", 382, "normal")
    return img


def thumb(level: str, variant: str, size: tuple[int, int]) -> Image.Image:
    base = draw_level(level, variant, hud=False, chars=False)
    return base.resize(size, Image.Resampling.NEAREST)


def screen_level_select(hover: int = 1) -> Image.Image:
    img = load(f"bg_menu_{DEFAULT['menu']}").copy()
    ui = DEFAULT["ui"]
    text(
        img,
        (W // 2, 70),
        "Select Level",
        font("jacquard", 72),
        RIM,
        "mm",
        shadow=CRIMSON,
        shadow_px=3,
    )
    card = load(f"ui_card_{ui}")
    cw, ch = 180, 224
    gap = 25
    x0 = (W - (3 * cw + 2 * gap)) // 2
    for i, level in enumerate(LEVELS):
        x = x0 + i * (cw + gap)
        y = (H - ch) // 2 + 30
        if i == hover:
            y -= 6
        framed = nine_slice(card, 20, (cw, ch))
        img.alpha_composite(framed, (x, y))
        t = thumb(level, DEFAULT[level], (cw - 52, (cw - 52) * 3 // 4))
        img.alpha_composite(t.convert("RGBA"), (x + 26, y + 70))
        text(
            img,
            (x + cw // 2, y + 32),
            f"LEVEL {i + 1}",
            font("silk", 8 * 2),
            BONE,
            "mm",
            shadow=None,
        )
        text(
            img,
            (x + cw // 2, y + 54),
            level.upper(),
            font("silk", 16),
            RIM,
            "mm",
            shadow=None,
        )
    text(img, (W // 2, 520), "CLICK A LEVEL TO PLAY", font("silk", 16), GOLD, "mm")
    return img


def screen_popup() -> Image.Image:
    img = load(f"bg_menu_{DEFAULT['menu']}").copy()
    menu_chars(img)
    panel = nine_slice(load(f"ui_panel_{DEFAULT['ui']}"), 20, (480, 300))
    img.alpha_composite(panel, ((W - 480) // 2, 150))
    text(
        img,
        (W // 2, 235),
        "Thanks for playing!",
        font("jacquard", 60),
        RIM,
        "mm",
        shadow=CRIMSON,
    )
    text(
        img,
        (W // 2, 290),
        "Click or press any key to hunt again",
        font("silk", 16),
        BONE,
        "mm",
    )
    button(img, "PLAY", 330, "hover")
    return img


# ------------------------------------------------------------------ sheets


def label_sheet(
    items: list[tuple[str, Image.Image]], cols: int, cell: tuple[int, int], title: str
) -> Image.Image:
    rows = (len(items) + cols - 1) // cols
    img = Image.new("RGB", (cols * cell[0], rows * (cell[1] + 18)), (24, 20, 28))
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    for i, (label, im) in enumerate(items):
        x, y = (i % cols) * cell[0], (i // cols) * (cell[1] + 18)
        im = im.convert("RGBA")
        scale = min((cell[0] - 8) / im.width, cell[1] / im.height)
        if scale < 1:
            im = im.resize(
                (int(im.width * scale), int(im.height * scale)),
                Image.Resampling.NEAREST,
            )
        tile = Image.new("RGB", cell, (60, 52, 68))
        tile.paste(im, ((cell[0] - im.width) // 2, (cell[1] - im.height) // 2), im)
        img.paste(tile, (x, y + 18))
        d.text((x + 4, y + 4), label, font=font("silk", 8), fill=BONE)
    return img


def sheet_backgrounds() -> None:
    items = []
    for lvl in ("menu", "classic", "towers", "arena"):
        for v in ("a", "b"):
            tag = " (default)" if DEFAULT[lvl] == v else ""
            items.append((f"{lvl} {v}{tag}".upper(), load(f"bg_{lvl}_{v}")))
    label_sheet(items, 4, (320, 240), "bgs").save(OUT / "19-backgrounds.png")


def sheet_levels() -> None:
    for lvl in ("classic", "towers", "arena"):
        parts = [
            (f"{lvl} {v}".upper(), draw_level(lvl, v, hud=False, chars=True))
            for v in ("a", "b")
        ]
        label_sheet(parts, 2, (636, 477), lvl).save(OUT / f"19-level-{lvl}.png")


def sheet_ui() -> None:
    items: list[tuple[str, Image.Image]] = []
    for v in ("a", "b"):
        for s in ("normal", "hover", "pressed"):
            items.append((f"button {v} {s}", load(f"ui_button_{v}_{s}")))
    for v in ("a", "b"):
        items.append((f"panel {v}", nine_slice(load(f"ui_panel_{v}"), 20, (320, 220))))
        items.append((f"card {v}", nine_slice(load(f"ui_card_{v}"), 20, (160, 200))))
    for n in ("arrow", "hand", "grab"):
        items.append(
            (
                f"cursor {n}",
                load(f"cursor_{n}").resize((56, 56), Image.Resampling.NEAREST),
            )
        )
    for n in ("3", "2", "1", "go"):
        items.append((f"digit {n}", load(f"digit_{n}")))
    label_sheet(items, 4, (320, 200), "ui").save(OUT / "19-ui-candidates.png")


def sheet_contact() -> None:
    """Every generated asset in assets/images/style/, one cell each."""
    items = [(f.stem, Image.open(f)) for f in sorted(STYLE.glob("*.png"))]
    label_sheet(items, 6, (210, 130), "all").save(OUT / "19-contact-sheet.png")


def sheet_fonts() -> None:
    img = Image.new("RGB", (1280, 380), (60, 52, 68))
    rows = [
        (
            "A: Jacquard 12 (titles only) + Silkscreen (buttons, HUD, labels)",
            "jacquard",
            60,
            "The Hunted  Select Level",
        ),
        ("", "silk", 24, "VAMPIRE  PEASANT  P1 0  Click to play  0123456789"),
        ("B: Press Start 2P everywhere", "press", 32, "THE HUNTED  Select level"),
        ("", "press", 16, "VAMPIRE  PEASANT  P1 0  Click to play  0123456789"),
        ("Today: Comic Neue", "comic", 40, "THE HUNTED  Select level  0123456789"),
    ]
    y = 8
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    for caption, kind, size, s in rows:
        if caption:
            d.text((10, y), caption.upper(), font=font("silk", 8), fill=GOLD)
            y += 16
        if kind == "comic":
            f = ImageFont.truetype(str(FONTS / "ComicNeue-Regular.ttf"), size)
        else:
            f = font(kind, size)
        d.text((10, y), s, font=f, fill=BONE)
        y += size + 22
    img.save(OUT / "19-fonts.png")


def sheet_palette() -> None:
    img = Image.new("RGB", (1280, 360), (24, 20, 28))
    d = ImageDraw.Draw(img)
    d.fontmode = "1"
    y = 10
    for title, ramps in (
        ("CORE (from the characters and icon)", palette.CORE),
        ("SCENERY", palette.SCENERY),
    ):
        d.text((10, y), title, font=font("silk", 8), fill=GOLD)
        y += 16
        for name, ramp in ramps.items():
            d.text(
                (10, y + 8), name.upper(), font=font("silk", 8), fill=BONE, anchor="lm"
            )
            for i, hx in enumerate(ramp):
                d.rectangle((90 + i * 44, y, 90 + i * 44 + 40, y + 16), fill=hx)
            y += 22
    img.save(OUT / "19-palette.png")


def readability() -> None:
    """Mean luma of each background's playing band vs the characters' bodies."""
    band = (int(H * 0.4), int(H * 0.9))
    rows = []
    for lvl in ("menu", "classic", "towers", "arena"):
        for v in ("a", "b"):
            a = np.asarray(load(f"bg_{lvl}_{v}").convert("L")).astype(float)
            seg = a[band[0] : band[1]]
            rows.append(
                f"{lvl} {v}: band luma mean {seg.mean():.0f}, min {seg.min():.0f}, max {seg.max():.0f}"
            )
    for role in ("vampire", "peasant"):
        c = np.asarray(character(role))
        body = c[c[..., 3] > 0][:, :3].astype(float)
        luma = body @ np.array([0.299, 0.587, 0.114])
        inner = luma[luma < 200]
        rows.append(f"{role} body (without rim) luma mean {inner.mean():.0f}")
    print("\n".join(rows))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    side_by_side(
        TODAY / "today_menu.png",
        screen_menu(("PLAY", "CREDITS", "EXIT")),
        "main menu",
        "main-menu",
    )
    side_by_side(
        TODAY / "today_menu.png",
        screen_menu(("VS AI", "PVP", "BACK"), 1),
        "mode menu",
        "mode-menu",
    )
    side_by_side(None, screen_credits(), "credits", "credits")
    side_by_side(
        TODAY / "today_level_select.png",
        screen_level_select(),
        "level select",
        "level-select",
    )
    for i, lvl in enumerate(LEVELS):
        side_by_side(
            TODAY / f"today_level{i}.png",
            draw_level(lvl, DEFAULT[lvl]),
            f"{lvl} in game",
            f"in-game-{lvl}",
        )
    side_by_side(None, screen_popup(), "web popup", "web-popup")
    sheet_backgrounds()
    sheet_levels()
    sheet_ui()
    sheet_contact()
    sheet_fonts()
    sheet_palette()
    readability()


if __name__ == "__main__":
    main()
