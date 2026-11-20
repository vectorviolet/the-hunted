"""Clean the raw Codex pictures up into game-ready pixel art (hard edges, shared palette).

    uv run --group art python scripts/art_gen/process.py [name ...]     # default: every raw picture

Needs Pillow and numpy, in the optional ``art`` dependency group: ``uv run --group art python
scripts/art_gen/process.py``. The game itself does not need them.
Reads ``scripts/art_gen/work/raw/<name>.png`` (written by generate.py, not committed),
writes ``assets/images/style/*.png``. Pixel scale is 2: art is made at half resolution, then
enlarged 2x with nearest neighbor, so one art pixel is 2x2 screen pixels (the characters are
drawn at 1x, see docs/design/art-style.md).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from PIL import Image
from prompts import JOBS

import palette

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
OUT = ROOT / "assets" / "images" / "style"
SCALE = 2
KEY = np.array([255, 0, 255])
KEY_DISTANCE = (
    150  # summed channel distance from magenta that still counts as background
)
INK = (
    28,
    11,
    24,
)  # violet-black; fills keyed-out pixels so resizing never bleeds magenta

# Readability grade for backgrounds (pass 2, night): mid-dark with real saturation. In the
# standing band (BAND rows, where the characters and platforms are) luma is held to
# BAND_LUMA: no near-black, nothing bright, and saturated red is toned down (red is the vampire's).
LUMA_LO, LUMA_HI = 40.0, 170.0
BAND_LUMA = (68.0, 125.0)
BAND = (0.4, 0.9)
SATURATION = 1.1

# Logical (half resolution) sizes.
BG_SIZE = (400, 300)
PLATFORM_HEIGHTS = {"classic": 25, "towers": 15, "arena": 10}  # screen 50 / 30 / 20
GROUND_HEIGHT = 25  # screen 50 (settings.GROUND_Y 550 to 600)
CAP, MID = (
    8,
    16,
)  # logical width of one platform cap and of the tiled middle (patch + mirror)
BUTTON_SIZE = (112, 32)
PANEL_SIZE = (200, 150)
CARD_SIZE = (90, 112)
CURSOR_HEIGHT = 14
DIGIT_HEIGHT = 40


def raw_path(name: str) -> Path:
    path = HERE / "work" / "raw" / f"{name}.png"
    if not path.exists():
        raise FileNotFoundError(name)
    return path


def snap(rgb: Image.Image) -> Image.Image:
    """Nearest palette color for every pixel, no dithering."""
    pal = Image.new("P", (1, 1))
    colors = palette.master()
    flat = [c for rgb_ in colors for c in rgb_]
    pal.putpalette(flat + [0] * (768 - len(flat)))
    return (
        rgb.convert("RGB")
        .quantize(palette=pal, dither=Image.Dither.NONE)
        .convert("RGB")
    )


def majority(img: Image.Image) -> Image.Image:
    """3x3 mode filter that removes single stray pixels left by the resize."""
    a = np.asarray(img)
    h, w, _ = a.shape
    pad = np.pad(a, ((1, 1), (1, 1), (0, 0)), mode="edge")
    out = a.copy()
    packed = (
        pad[:, :, 0].astype(np.int64) << 16
        | pad[:, :, 1].astype(np.int64) << 8
        | pad[:, :, 2].astype(np.int64)
    )
    stack = np.stack(
        [packed[dy : dy + h, dx : dx + w] for dy in range(3) for dx in range(3)]
    )
    center = stack[4]
    for y in range(h):
        for x in range(w):
            vals, counts = np.unique(stack[:, y, x], return_counts=True)
            best = vals[counts.argmax()]
            if counts.max() >= 6 and best != center[y, x]:
                out[y, x] = ((best >> 16) & 255, (best >> 8) & 255, best & 255)
    return Image.fromarray(out)


def enlarge(img: Image.Image) -> Image.Image:
    return img.resize((img.width * SCALE, img.height * SCALE), Image.Resampling.NEAREST)


def grade(img: Image.Image) -> Image.Image:
    a = np.asarray(img.convert("RGB")).astype(np.float64)
    h = a.shape[0]
    luma = a @ np.array([0.299, 0.587, 0.114])
    gray = luma[..., None]
    a = gray + (a - gray) * SATURATION
    target = LUMA_LO + (LUMA_HI - LUMA_LO) * (luma / 255.0)
    # Weight 1 inside the standing band, fading out over 8% of the height on both sides.
    rows = np.arange(h) / h
    fade = 0.08
    w = np.clip(
        np.minimum((rows - (BAND[0] - fade)) / fade, ((BAND[1] + fade) - rows) / fade),
        0,
        1,
    )[:, None]
    lo, hi = BAND_LUMA
    banded = np.clip(lo + (target - LUMA_LO) * (hi - lo) / (LUMA_HI - LUMA_LO), lo, hi)
    target = (1 - w) * target + w * banded
    a = a * (target / np.maximum(luma, 1.0))[..., None]
    # Tone down strong reds in the band so the cape does not blend into the scenery.
    red = (a[..., 0] - np.maximum(a[..., 1], a[..., 2])) > 50
    mix = np.where(red & (w > 0.5), 0.4, 1.0)[..., None]
    g2 = a @ np.array([0.299, 0.587, 0.114])
    a = g2[..., None] + (a - g2[..., None]) * mix
    return Image.fromarray(np.clip(a, 0, 255).astype(np.uint8))


def process_bg(name: str) -> None:
    img = Image.open(raw_path(name)).convert("RGB")
    w, h = img.size
    cw = round(h * 4 / 3)
    left = (w - cw) // 2
    img = img.crop((left, 0, left + cw, h))
    img = img.resize(BG_SIZE, Image.Resampling.BOX)
    img = majority(snap(grade(img)))
    enlarge(img).save(OUT / f"{name}.png")


def key_mask(img: Image.Image) -> np.ndarray:
    a = np.asarray(img.convert("RGB")).astype(int)
    return np.abs(a - KEY).sum(axis=2) > KEY_DISTANCE


SLAB_DIM = 0.78  # night grade for platforms and ground: moonlit, not bright


def cutout(
    img: Image.Image,
    size: tuple[int, int] | None = None,
    height: int | None = None,
    dim: float = 1.0,
) -> Image.Image:
    """Crop to the non-magenta part, resize (box), hard alpha, snap to the palette."""
    mask = key_mask(img)
    ys, xs = np.where(mask)
    box = (xs.min(), ys.min(), xs.max() + 1, ys.max() + 1)
    rgb = np.asarray(img.convert("RGB")).copy()
    rgb[~mask] = INK
    sub = Image.fromarray(rgb).crop(box)
    alpha = Image.fromarray((mask * 255).astype(np.uint8)).crop(box)
    if size is None:
        assert height is not None
        size = (max(1, round(sub.width * height / sub.height)), height)
    sub = sub.resize(size, Image.Resampling.BOX)
    if dim != 1.0:
        sub = Image.fromarray((np.asarray(sub) * dim).astype(np.uint8))
    alpha = alpha.resize(size, Image.Resampling.BOX).point(
        lambda v: 255 if v >= 128 else 0
    )
    out = snap(sub).convert("RGBA")
    out.putalpha(alpha)
    return out


def split_runs(mask: np.ndarray, axis: int, min_gap: int = 12) -> list[tuple[int, int]]:
    """Index ranges along ``axis`` that contain pixels, separated by gaps of empty lines."""
    occupied = mask.any(axis=1 - axis)
    runs: list[tuple[int, int]] = []
    start = None
    gap = 0
    for i, on in enumerate(occupied):
        if on:
            if start is None:
                start = i
            gap = 0
            end = i + 1
        elif start is not None:
            gap += 1
            if gap >= min_gap:
                runs.append((start, end))
                start = None
    if start is not None:
        runs.append((start, end))
    return [r for r in runs if r[1] - r[0] > 20]


def parts(img: Image.Image, axis: int) -> list[Image.Image]:
    """Cut a sheet into its separate items (axis 0 = stacked vertically, 1 = side by side)."""
    mask = key_mask(img)
    out = []
    for a, b in split_runs(mask, axis):
        box = (0, a, img.width, b) if axis == 0 else (a, 0, b, img.height)
        out.append(img.crop(box))
    return out


def process_slab(name: str) -> None:
    level = name.removeprefix("slab_")
    raw = Image.open(raw_path(name))
    for kind, height in (
        ("platform", PLATFORM_HEIGHTS[level]),
        ("ground", GROUND_HEIGHT),
    ):
        slab = cutout(raw, height=height, dim=SLAB_DIM)
        # 3-slice sheet: left cap | middle (patch + its mirror, so it tiles seamlessly) | right cap
        patch_w = MID // 2
        mid_x = (slab.width - patch_w) // 2
        patch = slab.crop((mid_x, 0, mid_x + patch_w, height))
        sheet = Image.new("RGBA", (CAP + MID + CAP, height))
        sheet.paste(slab.crop((0, 0, CAP, height)), (0, 0))
        sheet.paste(patch, (CAP, 0))
        sheet.paste(
            patch.transpose(Image.Transpose.FLIP_LEFT_RIGHT), (CAP + patch_w, 0)
        )
        sheet.paste(
            slab.crop((slab.width - CAP, 0, slab.width, height)), (CAP + MID, 0)
        )
        enlarge(sheet).save(OUT / f"{kind}_{level}.png")


def process_buttons(name: str) -> None:
    variant = name.removeprefix("ui_buttons_")
    items = parts(Image.open(raw_path(name)).convert("RGB"), axis=0)
    assert len(items) == 3, f"{name}: found {len(items)} buttons"
    for state, item in zip(("normal", "hover", "pressed"), items, strict=True):
        enlarge(cutout(item, size=BUTTON_SIZE)).save(
            OUT / f"ui_button_{variant}_{state}.png"
        )


def process_panel(name: str) -> None:
    variant = name.removeprefix("ui_panel_")
    items = parts(Image.open(raw_path(name)).convert("RGB"), axis=1)
    assert len(items) == 2, f"{name}: found {len(items)} frames"
    # The larger frame is the popup panel, the other the level-select card.
    items.sort(key=lambda i: i.width, reverse=True)
    enlarge(cutout(items[0], size=PANEL_SIZE)).save(OUT / f"ui_panel_{variant}.png")
    enlarge(cutout(items[1], size=CARD_SIZE)).save(OUT / f"ui_card_{variant}.png")


def process_cursor(name: str) -> None:
    items = parts(Image.open(raw_path(name)).convert("RGB"), axis=1)
    assert len(items) == 3, f"{name}: found {len(items)} cursors"
    for label, item in zip(("arrow", "hand", "grab"), items, strict=True):
        enlarge(cutout(item, height=CURSOR_HEIGHT)).save(OUT / f"cursor_{label}.png")


def process_digits(name: str) -> None:
    items = parts(Image.open(raw_path(name)).convert("RGB"), axis=1)
    assert len(items) == 4, f"{name}: found {len(items)} glyphs"
    for label, item in zip(("3", "2", "1", "go"), items, strict=True):
        enlarge(cutout(item, height=DIGIT_HEIGHT)).save(OUT / f"digit_{label}.png")


HANDLERS = {
    "bg": process_bg,
    "slab": process_slab,
    "ui_buttons": process_buttons,
    "ui_panel": process_panel,
    "ui_cursor": process_cursor,
    "ui_digits": process_digits,
}


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[1:] or list(JOBS):
        try:
            raw_path(name)
        except FileNotFoundError:
            print(f"{name}: no raw picture yet")
            continue
        HANDLERS[JOBS[name][0]](name)
        print(f"{name}: done")


if __name__ == "__main__":
    main()
