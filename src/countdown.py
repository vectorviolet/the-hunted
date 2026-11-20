"""The pre-game countdown graphic (3, 2, 1, 0, GO), drawn in code.

`countdown_step` holds the pure logic (what is shown at a given countdown value) so it can be tested
without a window; `CountdownGraphic` draws one step.
"""

import math
from dataclasses import dataclass

import pygame

from settings import FONT

ORANGE = (255, 100, 0)
TEAL = (52, 219, 169)
TEXT_COLOR = (0, 0, 0)

SIZE = 300                  # the graphic is a SIZE x SIZE square ...
POSITION = (250, 30)        # ... blitted here
DIGIT_FRAMES = 12           # frames per digit (0.2 s at 60 FPS, one update per frame)
GO_FRAME = 48               # first frame of "GO" (after the digits 3, 2, 1, 0)
END_FRAME = 60              # the countdown ends here (the game moves on to level select); the
                            # idle value Game uses before a countdown starts must be >= this
_RING_COLORS = (ORANGE, TEAL)

_SUPERSAMPLE = 2            # the ring is drawn at this many times the size, then scaled down
RING_OUTER = 123           # ring outer radius at SIZE
RING_WIDTH = 14
_DIGIT_FONT_SIZE = 156      # the digit is about 106 px tall
_GO_FONT_SIZE = 120


@dataclass(frozen=True)
class CountdownStep:
    """What the countdown shows at one frame."""

    label: str
    fraction: float                       # share of the ring drawn in `color`, clockwise from the top
    color: tuple[int, int, int] | None    # None for "GO", which has no ring
    base_color: tuple[int, int, int] | None = None  # a full ring drawn underneath, if any


# Ring progress for the first frames of each digit (3, 2, 1, 0), measured from the original frames
# (normalized so the ring is full at the end); frames after the table are full.
_FILL = (
    (0.43, 0.60, 0.75, 0.82, 0.89, 0.93, 0.96, 0.98, 1.0),
    (0.30, 0.52, 0.70, 0.78, 0.86, 0.91, 0.95, 0.97, 0.99),
    (0.16, 0.43, 0.66, 0.75, 0.84, 0.89, 0.94, 0.96, 0.98),
    (0.06, 0.30, 0.59, 0.70, 0.82, 0.87, 0.94, 0.96, 0.99),
)


def _fill(index: int, frame_in_digit: int) -> float:
    """Ring progress within one digit (index 0 is the digit 3): fast at first, then slowing down."""
    table = _FILL[index]
    return table[frame_in_digit] if frame_in_digit < len(table) else 1.0


def countdown_step(countdown: int) -> CountdownStep | None:
    """The step to draw for a countdown value, or None when nothing is shown."""
    if not 0 < countdown < END_FRAME:
        return None
    if countdown >= GO_FRAME:
        return CountdownStep("GO", 0.0, None)
    index, frame_in_digit = divmod(countdown, DIGIT_FRAMES)
    base = _RING_COLORS[(index - 1) % 2] if index > 0 else None
    return CountdownStep(
        str(3 - index), _fill(index, frame_in_digit), _RING_COLORS[index % 2], base
    )


class CountdownGraphic:
    """Draws a `CountdownStep` into a SIZE x SIZE square (each distinct step is rendered once)."""

    def __init__(self) -> None:
        self._digit_font = pygame.font.Font(FONT, _DIGIT_FONT_SIZE)
        self._digit_font.bold = True
        self._go_font = pygame.font.Font(FONT, _GO_FONT_SIZE)
        self._go_font.bold = True
        self._images: dict[CountdownStep, pygame.Surface] = {}  # finished graphics, built on first use
        self._labels = {
            label: font.render(label, True, TEXT_COLOR)
            for label, font in (
                *((str(d), self._digit_font) for d in range(4)),
                ("GO", self._go_font),
            )
        }

    def draw(self, surface: pygame.Surface, step: CountdownStep) -> None:
        image = self._images.get(step)
        if image is None:
            image = self._images[step] = self._render(step)
        surface.blit(image, POSITION)

    def _render(self, step: CountdownStep) -> pygame.Surface:
        image = pygame.Surface((SIZE, SIZE), pygame.SRCALPHA)
        if step.color is not None:
            image.blit(self._ring(step), (0, 0))
        text = self._labels[step.label]
        image.blit(text, text.get_rect(center=(SIZE // 2, SIZE // 2)))
        return image

    @staticmethod
    def _ring(step: CountdownStep) -> pygame.Surface:
        assert step.color is not None
        scale = _SUPERSAMPLE
        big = pygame.Surface((SIZE * scale, SIZE * scale), pygame.SRCALPHA)
        center = SIZE * scale // 2
        outer = RING_OUTER * scale
        width = RING_WIDTH * scale
        rect = pygame.Rect(0, 0, outer * 2, outer * 2)
        rect.center = (center, center)
        if step.base_color is not None:
            pygame.draw.arc(big, step.base_color, rect, 0, 2 * math.pi, width)
        # pygame arcs run counterclockwise from 3 o'clock; the ring fills clockwise from 12 o'clock.
        top = math.pi / 2
        start = top - step.fraction * 2 * math.pi
        pygame.draw.arc(big, step.color, rect, start, top, width)
        if 0 < step.fraction < 1:
            # Round caps, like the original frames.
            mid = outer - width / 2
            for angle in (start, top):
                cap = (center + mid * math.cos(angle), center - mid * math.sin(angle))
                pygame.draw.circle(big, step.color, cap, width / 2)
        return pygame.transform.smoothscale(big, (SIZE, SIZE))
