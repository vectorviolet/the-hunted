import pygame
import pytest

import settings
from background import load_background

NAMES = [level["background"] for level in settings.LEVELS] + [settings.MENU_BACKGROUND]


@pytest.mark.parametrize("name", NAMES)
def test_every_backdrop_is_a_full_screen_picture(name):
    image = load_background(name, (800, 600))

    assert image.get_size() == (800, 600)
    assert image.get_alpha() is None  # opaque


def test_a_backdrop_is_loaded_once_per_size():
    assert load_background("menu", (800, 600)) is load_background("menu", (800, 600))


def test_another_size_is_scaled_without_inventing_colors():
    original = load_background("menu", (800, 600))
    small = load_background("menu", (400, 300))

    assert small.get_size() == (400, 300)
    # Nearest-neighbor: no color appears that the original picture does not have.
    colors = {
        tuple(original.get_at((x, y))) for x in range(800) for y in range(0, 600, 3)
    }
    sample = {tuple(small.get_at((x, y))) for x in range(400) for y in range(300)}
    assert sample <= colors


def test_each_level_has_its_own_backdrop_and_the_menu_another():
    assert len(set(NAMES)) == len(NAMES)
    pictures = {
        pygame.image.tobytes(load_background(n, (800, 600)), "RGB") for n in NAMES
    }
    assert len(pictures) == len(NAMES)
