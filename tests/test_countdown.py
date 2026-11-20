import pygame
import pytest

from countdown import (
    ORANGE,
    POSITION,
    SIZE,
    TEAL,
    CountdownGraphic,
    CountdownStep,
    countdown_step,
)


@pytest.mark.parametrize("countdown", [-1, 0, 60, 99, 100])
def test_nothing_is_shown_outside_the_countdown(countdown):
    assert countdown_step(countdown) is None


@pytest.mark.parametrize(
    "countdown, label",
    [(1, "3"), (11, "3"), (12, "2"), (23, "2"), (24, "1"), (35, "1"), (36, "0"), (47, "0"),
     (48, "GO"), (59, "GO")],
)
def test_digit_sequence(countdown, label):
    step = countdown_step(countdown)
    assert step is not None
    assert step.label == label


def test_ring_colors_alternate_each_second_over_the_previous_ring():
    colors = [(countdown_step(c).color, countdown_step(c).base_color) for c in (1, 13, 25, 37)]
    assert colors == [(ORANGE, None), (TEAL, ORANGE), (ORANGE, TEAL), (TEAL, ORANGE)]


def test_ring_fills_within_each_second_and_restarts_for_the_next_digit():
    for first in (1, 12, 24, 36):
        fractions = [countdown_step(first + i).fraction for i in range(11 if first == 1 else 12)]
        assert fractions == sorted(fractions)
        assert 0 < fractions[0] < 0.5
        assert fractions[-1] == 1.0
    assert countdown_step(12).fraction < countdown_step(11).fraction


def test_go_has_no_ring():
    step = countdown_step(50)
    assert step == CountdownStep("GO", 0.0, None)


def _opaque_ring_pixels(surface):
    # Pixels along the ring's mid radius, at 12, 3, 6 and 9 o'clock.
    x0, y0 = POSITION
    c, r = SIZE // 2, 116
    return [surface.get_at((x0 + c + dx, y0 + c + dy))[:3] for dx, dy in
            ((0, -r), (r, 0), (0, r), (-r, 0))]


def test_draw_paints_the_ring_where_the_fraction_says():
    graphic = CountdownGraphic()
    surface = pygame.Surface((800, 600))
    surface.fill((10, 20, 30))

    graphic.draw(surface, CountdownStep("3", 0.5, ORANGE))

    _top, right, bottom, left = _opaque_ring_pixels(surface)
    assert right == bottom == ORANGE      # clockwise from the top: the right half is filled
    assert left == (10, 20, 30)           # the left half is empty


def test_draw_go_leaves_the_ring_area_untouched():
    graphic = CountdownGraphic()
    surface = pygame.Surface((800, 600))
    surface.fill((10, 20, 30))

    graphic.draw(surface, CountdownStep("GO", 0.0, None))

    assert set(_opaque_ring_pixels(surface)) == {(10, 20, 30)}
