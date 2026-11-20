"""The pre-game countdown (3, 2, 1, GO!), drawn from the glyph art in assets/images/countdown/.

`countdown_step` holds the pure logic (what is shown at a given countdown value) so it can be
tested without a window; `CountdownGraphic` draws one step.
"""

from dataclasses import dataclass

import pygame

CENTER = (480, 150)  # the glyph is centered here
STEP_FRAMES = 15  # frames per glyph (0.25 s at 60 FPS, one update per frame)
LABELS = ("3", "2", "1", "GO")
END_FRAME = STEP_FRAMES * len(
    LABELS
)  # the countdown ends here (the game moves on to level select); the
# idle value Game uses before a countdown starts must be >= this
# Each glyph drops in: its vertical offset in px (multiples of 2, the art's pixel size) for the
# first frames, then it rests.
_DROP = (-24, -16, -10, -6, -2)

_FILES = {"3": "3", "2": "2", "1": "1", "GO": "go"}


@dataclass(frozen=True)
class CountdownStep:
    """What the countdown shows at one frame."""

    label: str  # "3", "2", "1" or "GO"
    offset: int  # vertical offset in px while the glyph drops in; 0 at rest


def countdown_step(countdown: int) -> CountdownStep | None:
    """The step to draw for a countdown value, or None when nothing is shown."""
    if not 0 < countdown < END_FRAME:
        return None
    index, frame = divmod(countdown, STEP_FRAMES)
    if index == 0:
        frame -= 1  # the countdown is first drawn at 1, so "3" starts its drop too
    return CountdownStep(LABELS[index], _DROP[frame] if frame < len(_DROP) else 0)


class CountdownGraphic:
    """Draws a `CountdownStep`: the glyph's art, centered, dropping in."""

    def __init__(self) -> None:
        self._glyphs = {
            label: pygame.image.load(
                f"assets/images/countdown/{file}.png"
            ).convert_alpha()
            for label, file in _FILES.items()
        }

    def draw(self, surface: pygame.Surface, step: CountdownStep) -> None:
        glyph = self._glyphs[step.label]
        center = (CENTER[0], CENTER[1] + step.offset)
        surface.blit(glyph, glyph.get_rect(center=center))
