"""Menu button images: Kenney UI Pack button art with the label drawn in the game font."""

import pygame

from settings import FONT

# Kenney UI Pack "rectangle" buttons are 192x64 with rounded corners. The corners keep
# their proportions when the button is resized; only the middle is stretched.
SOURCE_SIZE = (192, 64)
CAP = 20  # width in source pixels of each rounded end
EDGE = 4  # source pixels of bottom edge on the raised buttons; the pressed one has none

BTN_NORMAL, BTN_PRESSED, BTN_HOVER = range(
    3
)  # state indexes into the lists Menu builds
IMAGE_FILES = {
    BTN_NORMAL: "button_rectangle_depth_gradient.png",
    BTN_PRESSED: "button_rectangle_gradient.png",
    BTN_HOVER: "button_rectangle_depth_gloss.png",
}
LABEL_COLOR = (255, 255, 255)
SHADOW_COLOR = (0, 0, 0)


def load_button(state: int, size: tuple[int, int]) -> pygame.Surface:
    """The button art for `state`, scaled to `size` (corners keep their proportions)."""
    source = pygame.image.load(f"assets/images/buttons/{IMAGE_FILES[state]}")
    assert source.get_size() == SOURCE_SIZE
    width, height = size
    scale = height / SOURCE_SIZE[1]
    cap = round(CAP * scale)
    middle = width - 2 * cap
    assert middle > 0, "button is too narrow for its rounded ends"
    src_w, src_h = SOURCE_SIZE
    result = pygame.Surface(size, pygame.SRCALPHA)
    parts = (
        (pygame.Rect(0, 0, CAP, src_h), (0, 0), (cap, height)),
        (pygame.Rect(CAP, 0, src_w - 2 * CAP, src_h), (cap, 0), (middle, height)),
        (pygame.Rect(src_w - CAP, 0, CAP, src_h), (cap + middle, 0), (cap, height)),
    )
    for area, pos, part_size in parts:
        piece = source.subsurface(area)
        result.blit(pygame.transform.smoothscale(piece, part_size), pos)
    return result


def make_button(
    state: int, size: tuple[int, int], label: str, font_size: int
) -> pygame.Surface:
    """A button image in `state` with `label` centered on it (shifted down when pressed)."""
    button = load_button(state, size)
    font = pygame.font.Font(FONT, font_size)
    text = font.render(label, True, LABEL_COLOR)
    shadow = font.render(label, True, SHADOW_COLOR)
    # Raised buttons have a bottom edge, so their face is a little shorter than the pressed one.
    edge = 0 if state == BTN_PRESSED else round(EDGE * size[1] / SOURCE_SIZE[1])
    center = (size[0] // 2, (size[1] - edge) // 2)
    offset = max(1, size[1] // 40)
    button.blit(
        shadow, shadow.get_rect(center=(center[0] + offset, center[1] + offset))
    )
    button.blit(text, text.get_rect(center=center))
    return button
