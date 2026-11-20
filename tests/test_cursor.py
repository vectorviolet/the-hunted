import pygame
import pytest

from cursor import CLICK, CLICK2, HELP, NORMAL, WRITING, Cursor

STATES = (NORMAL, CLICK, CLICK2, HELP, WRITING)


def test_starts_in_the_normal_state_with_the_size_of_its_image():
    cursor = Cursor()

    assert cursor.state == NORMAL
    assert cursor.rect.size == (32, 32)


@pytest.mark.parametrize("state", STATES)
def test_set_state_switches_to_every_known_state(state):
    cursor = Cursor()

    cursor.set_state(state)

    assert cursor.state == state


def test_set_state_rejects_an_unknown_state_and_keeps_the_old_one():
    cursor = Cursor()
    cursor.set_state(CLICK)

    with pytest.raises(AssertionError):
        cursor.set_state("pikachu")

    assert cursor.state == CLICK


@pytest.mark.parametrize(
    ("state", "tip"),
    [
        (NORMAL, "topleft"),  # the arrow's tip is its top-left corner
        (CLICK, "midtop"),  # the pointing finger is the top of the hand
        (HELP, "topleft"),
    ],
)
def test_draw_puts_the_tip_on_the_mouse_position(state, tip):
    cursor = Cursor()
    cursor.set_state(state)
    cursor.rect.x, cursor.rect.y = 40, 40
    surface = pygame.Surface((100, 100), pygame.SRCALPHA)

    cursor.draw(surface)

    bounds = surface.get_bounding_rect()
    tip_x, tip_y = getattr(bounds, tip)
    assert abs(tip_y - 40) <= 1
    assert abs(tip_x - 40) <= (10 if tip == "midtop" else 3)


@pytest.mark.parametrize("state", (CLICK2, WRITING))
def test_draw_centers_the_round_cursors_on_the_mouse_position(state):
    cursor = Cursor()
    cursor.set_state(state)
    cursor.rect.x, cursor.rect.y = 40, 40
    surface = pygame.Surface((100, 100), pygame.SRCALPHA)

    cursor.draw(surface)

    cx, cy = surface.get_bounding_rect().center
    assert abs(cx - 40) <= 2
    assert abs(cy - 40) <= 2


def test_each_state_draws_a_different_image():
    drawn = {}
    for state in STATES:
        cursor = Cursor()
        cursor.set_state(state)
        cursor.rect.x, cursor.rect.y = 40, 40
        surface = pygame.Surface((100, 100), pygame.SRCALPHA)
        cursor.draw(surface)
        drawn[state] = pygame.image.tobytes(surface, "RGBA")

    assert len(set(drawn.values())) == len(STATES)
