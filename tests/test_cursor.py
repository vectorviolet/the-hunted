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


@pytest.mark.parametrize("state", STATES)
def test_draw_puts_the_hotspot_on_the_mouse_position(state):
    cursor = Cursor()
    cursor.set_state(state)
    cursor.rect.x, cursor.rect.y = 40, 40
    surface = pygame.Surface((100, 100), pygame.SRCALPHA)

    cursor.draw(surface)

    # The image is drawn where its own pixels say: its opaque part must cover the
    # mouse position (the hotspot) -- for the arrow, the tip is right on it.
    assert surface.get_at((40, 40))[3] > 0
    assert surface.get_bounding_rect().collidepoint(40, 40)


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
