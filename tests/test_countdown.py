import pygame
import pytest

from countdown import (
    CENTER,
    END_FRAME,
    STEP_FRAMES,
    CountdownGraphic,
    CountdownStep,
    countdown_step,
)


@pytest.mark.parametrize("countdown", [-1, 0, END_FRAME, 99, 100])
def test_nothing_is_shown_outside_the_countdown(countdown):
    assert countdown_step(countdown) is None


@pytest.mark.parametrize(
    "countdown, label",
    [
        (1, "3"),
        (14, "3"),
        (15, "2"),
        (29, "2"),
        (30, "1"),
        (44, "1"),
        (45, "GO"),
        (59, "GO"),
    ],
)
def test_glyph_sequence(countdown, label):
    step = countdown_step(countdown)
    assert step is not None
    assert step.label == label


def test_the_countdown_is_four_equal_steps_filling_the_old_length():
    assert END_FRAME == 4 * STEP_FRAMES == 60


def test_a_glyph_drops_in_and_then_rests():
    steps = [countdown_step(STEP_FRAMES + i) for i in range(STEP_FRAMES)]
    offsets = [step.offset for step in steps if step is not None]
    assert len(offsets) == STEP_FRAMES
    assert offsets[0] < 0  # starts above its resting place
    assert offsets == sorted(offsets)  # moves down, never back up
    assert offsets[-1] == 0  # at rest for the rest of the step
    assert all(offset % 2 == 0 for offset in offsets)  # whole art pixels (2 px each)


def test_every_glyph_starts_its_drop_at_the_same_height():
    firsts = [countdown_step(1), *(countdown_step(i * STEP_FRAMES) for i in (1, 2, 3))]
    offsets = [step.offset for step in firsts if step is not None]
    assert len(offsets) == 4
    assert len(set(offsets)) == 1 and offsets[0] < 0


def _painted_bounds(label: str, offset: int = 0) -> pygame.Rect:
    surface = pygame.Surface((960, 540), pygame.SRCALPHA)
    CountdownGraphic().draw(surface, CountdownStep(label, offset))
    return surface.get_bounding_rect()


@pytest.mark.parametrize("label", ["3", "2", "1", "GO"])
def test_every_glyph_is_drawn_centered_on_the_countdown_spot(label):
    bounds = _painted_bounds(label)

    assert bounds.width > 0
    assert abs(bounds.centerx - CENTER[0]) <= 1
    assert abs(bounds.centery - CENTER[1]) <= 1


def test_the_offset_moves_the_glyph_vertically():
    rest = _painted_bounds("3")
    dropped = _painted_bounds("3", offset=-24)

    assert dropped.top == rest.top - 24
    assert dropped.left == rest.left


def test_the_glyphs_look_different():
    images = set()
    for label in ("3", "2", "1", "GO"):
        surface = pygame.Surface((960, 540))
        CountdownGraphic().draw(surface, CountdownStep(label, 0))
        images.add(pygame.image.tobytes(surface, "RGB"))
    assert len(images) == 4
