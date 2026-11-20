"""Menu button images: the forged-iron button art with the label drawn in the UI font."""

import functools

import pygame

import settings
from pixelart import nine_slice

SOURCE_SIZE = (224, 64)  # every state's art is this size
BORDER = 14  # px of each corner and edge that is kept as drawn (rivets, bevel); the face stretches

BTN_NORMAL, BTN_PRESSED, BTN_HOVER = range(3)  # the states a button can be drawn in
IMAGE_FILES = {
    BTN_NORMAL: "button_normal.png",
    BTN_PRESSED: "button_pressed.png",
    BTN_HOVER: "button_hover.png",
}
LABEL_OFFSET = 2  # a pressed button's label sits this much lower (one art pixel)

BUTTON_SIZE = (212, 44)  # the size of every menu button but the wide ones
BUTTON_FONT = 24  # Silkscreen size of a button's label: a multiple of its 8 px grid
BACK_TOP = (
    425  # the level select's BACK button (menu.py places the others page by page)
)


def centered_button_rect(top: int, size: tuple[int, int] = BUTTON_SIZE) -> pygame.Rect:
    """The rect of a button of `size` centered on the canvas, `top` px from its top."""
    return pygame.Rect((settings.VIRTUAL_W - size[0]) // 2, top, *size)


@functools.cache
def _source(state: int) -> pygame.Surface:
    source = pygame.image.load(f"assets/images/ui/{IMAGE_FILES[state]}").convert_alpha()
    assert source.get_size() == SOURCE_SIZE
    return source


@functools.cache
def _font(size: int) -> pygame.font.Font:
    return pygame.font.Font(settings.UI_FONT, size)


def load_button(state: int, size: tuple[int, int]) -> pygame.Surface:
    """The button art for `state`, stretched to `size` (the corners keep their pixels)."""
    return nine_slice(_source(state), BORDER, size)


def make_button(
    state: int, size: tuple[int, int], label: str, font_size: int
) -> pygame.Surface:
    """A button image in `state` with `label` centered on its face.

    `font_size` should be a multiple of 8 (Silkscreen's pixel grid).
    """
    button = load_button(state, size)
    font = _font(font_size)
    text = font.render(label, False, settings.BONE)
    shadow = font.render(label, False, settings.INK)
    drop = LABEL_OFFSET if state == BTN_PRESSED else 0
    center = (size[0] // 2, size[1] // 2 - 2 + drop)
    button.blit(shadow, shadow.get_rect(center=(center[0] + 2, center[1] + 2)))
    button.blit(text, text.get_rect(center=center))
    return button
