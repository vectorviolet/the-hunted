"""Menu button images: Kenney UI Pack button art with the label drawn in the game font."""

import functools

import pygame

from settings import FONT

# Kenney UI Pack "rectangle" buttons are 192x64 with rounded corners. The corners keep
# their proportions when the button is resized; only the middle is stretched.
SOURCE_SIZE = (192, 64)
CAP = 20  # width in source pixels of each rounded end
EDGE = (
    4  # source pixels of the bottom edge on the raised buttons; pressed ones sink by it
)

BTN_NORMAL, BTN_PRESSED, BTN_HOVER = range(3)  # the states a button can be drawn in
IMAGE_FILES = {
    BTN_NORMAL: "button_rectangle_depth_gradient.png",
    BTN_PRESSED: "button_rectangle_gradient.png",
    BTN_HOVER: "button_rectangle_depth_gloss.png",
}
LABEL_COLOR = (255, 255, 255)
SHADOW_COLOR = (0, 0, 0)


@functools.cache
def _source(state: int) -> pygame.Surface:
    source = pygame.image.load(f"assets/images/buttons/{IMAGE_FILES[state]}")
    assert source.get_size() == SOURCE_SIZE
    return source


@functools.cache
def _font(size: int) -> pygame.font.Font:
    return pygame.font.Font(FONT, size)


def _edge(height: int) -> int:
    """Height in pixels of the bottom edge of a raised button `height` pixels tall."""
    return round(EDGE * height / SOURCE_SIZE[1])


def load_button(state: int, size: tuple[int, int]) -> pygame.Surface:
    """The button art for `state`, scaled to `size` (corners keep their proportions).

    A pressed button is the flat art drawn `edge` pixels lower, so the whole face drops
    into the space the raised buttons use for their bottom edge.
    """
    source = _source(state)
    width, height = size
    edge = _edge(height)
    top = edge if state == BTN_PRESSED else 0
    art_h = height - top
    cap = round(CAP * height / SOURCE_SIZE[1])
    middle = width - 2 * cap
    assert middle > 0, "button is too narrow for its rounded ends"
    src_w, src_h = SOURCE_SIZE
    result = pygame.Surface(size, pygame.SRCALPHA)
    parts = (
        (pygame.Rect(0, 0, CAP, src_h), (0, top), (cap, art_h)),
        (pygame.Rect(CAP, 0, src_w - 2 * CAP, src_h), (cap, top), (middle, art_h)),
        (pygame.Rect(src_w - CAP, 0, CAP, src_h), (cap + middle, top), (cap, art_h)),
    )
    for area, pos, part_size in parts:
        piece = source.subsurface(area)
        result.blit(pygame.transform.smoothscale(piece, part_size), pos)
    return result


def make_button(
    state: int, size: tuple[int, int], label: str, font_size: int
) -> pygame.Surface:
    """A button image in `state` with `label` centered on its face."""
    button = load_button(state, size)
    font = _font(font_size)
    text = font.render(label, True, LABEL_COLOR)
    shadow = font.render(label, True, SHADOW_COLOR)
    edge = _edge(size[1])
    # The face is the button without its bottom edge; a pressed button's face is lower.
    top = edge if state == BTN_PRESSED else 0
    center = (size[0] // 2, top + (size[1] - edge) // 2)
    offset = max(1, size[1] // 40)
    button.blit(
        shadow, shadow.get_rect(center=(center[0] + offset, center[1] + offset))
    )
    button.blit(text, text.get_rect(center=center))
    return button
