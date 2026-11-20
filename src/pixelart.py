"""Slicing helpers for the pixel art: stretch a picture to any size without blurring or
distorting its corners. Everything here uses nearest-neighbor scaling and plain blits, so the
pixels stay hard-edged.
"""

import pygame

STRIP_CAP = 16  # width of each end cap of a platform/ground strip sheet
STRIP_MID = 32  # width of its tiled middle (a patch followed by its mirror image)


def three_slice(
    sheet: pygame.Surface, width: int, cap: int = STRIP_CAP, mid: int = STRIP_MID
) -> pygame.Surface:
    """A strip `width` px wide from a `cap | mid | cap` sheet: the caps at the ends and the
    middle repeated between them (the last repeat is cut off).

    `width` must leave room for both caps.
    """
    assert sheet.get_width() == 2 * cap + mid, "sheet is not cap | middle | cap"
    assert width >= 2 * cap, f"a strip needs at least {2 * cap} px, not {width}"
    height = sheet.get_height()
    strip = pygame.Surface((width, height), pygame.SRCALPHA)
    strip.blit(sheet, (0, 0), (0, 0, cap, height))
    x = cap
    while x < width - cap:
        piece = min(mid, width - cap - x)
        strip.blit(sheet, (x, 0), (cap, 0, piece, height))
        x += piece
    strip.blit(sheet, (width - cap, 0), (cap + mid, 0, cap, height))
    return strip


def nine_slice(
    image: pygame.Surface, border: int, size: tuple[int, int]
) -> pygame.Surface:
    """`image` stretched to `size`: the four corners stay as they are, the edges and the
    middle stretch (nearest-neighbor)."""
    src_w, src_h = image.get_size()
    width, height = size
    assert width >= 2 * border and height >= 2 * border, (
        f"{size} is too small for a {border} px border"
    )
    assert src_w > 2 * border and src_h > 2 * border, "image is smaller than its border"
    result = pygame.Surface(size, pygame.SRCALPHA)
    # (source start, source end, destination start, destination end) of the three bands
    xs = [
        (0, border, 0, border),
        (border, src_w - border, border, width - border),
        (src_w - border, src_w, width - border, width),
    ]
    ys = [
        (0, border, 0, border),
        (border, src_h - border, border, height - border),
        (src_h - border, src_h, height - border, height),
    ]
    for sx0, sx1, dx0, dx1 in xs:
        for sy0, sy1, dy0, dy1 in ys:
            if dx1 <= dx0 or dy1 <= dy0:
                continue
            piece = image.subsurface((sx0, sy0, sx1 - sx0, sy1 - sy0))
            if piece.get_size() != (dx1 - dx0, dy1 - dy0):
                piece = pygame.transform.scale(piece, (dx1 - dx0, dy1 - dy0))
            result.blit(piece, (dx0, dy0))
    return result
