import pygame

from pygamine import GameObject

NORMAL = "normal"
CLICK = "click"  # over something clickable
CLICK2 = "click2"  # pressing it
HELP = "help"
WRITING = "writing"

# State -> (image file, hotspot). The hotspot is the pixel of the image that sits on the
# mouse position: the arrow's tip, the pointing finger's tip, or the middle of the others.
_IMAGES: dict[str, tuple[str, tuple[int, int]]] = {
    NORMAL: ("pointer_a", (9, 6)),
    CLICK: ("hand_point", (9, 2)),
    CLICK2: ("hand_closed", (16, 16)),
    HELP: ("cursor_help", (4, 1)),
    WRITING: ("bracket_a_vertical", (16, 16)),
}


class Cursor(GameObject):
    def __init__(self) -> None:
        super().__init__()
        self._images = {
            state: pygame.image.load(f"assets/images/cursor/{name}.png")
            for state, (name, _) in _IMAGES.items()
        }
        self._state = NORMAL
        self.rect.size = self._images[NORMAL].get_size()

    @property
    def state(self) -> str:
        return self._state

    def set_state(self, state: str) -> None:
        assert state in _IMAGES, f"unknown cursor state {state!r}"
        self._state = state

    def draw(self, surface: pygame.Surface) -> None:
        hot_x, hot_y = _IMAGES[self._state][1]
        surface.blit(
            self._images[self._state], (self.rect.x - hot_x, self.rect.y - hot_y)
        )
