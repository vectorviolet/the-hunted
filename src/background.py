"""The full-screen backdrops: one finished 800x600 picture per level and for the menu."""

import functools

import pygame

_DIR = "assets/images/background"


@functools.cache
def load_background(name: str, size: tuple[int, int]) -> pygame.Surface:
    """`assets/images/background/<name>.png`, as an opaque surface of `size`.

    The art is already 800x600; any other size is scaled with nearest-neighbor.
    Cached per name and size, so a picture is read from disk once.
    """
    image = pygame.image.load(f"{_DIR}/{name}.png").convert()
    if image.get_size() != size:
        image = pygame.transform.scale(image, size)
    return image
