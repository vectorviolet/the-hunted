import pygame
import pytest

from input_handler import KeyboardInputHandler


class FakeKeys:
    """Stands in for pygame.key.get_pressed(): only the given keys read as down."""

    def __init__(self, *down: int) -> None:
        self._down = set(down)

    def __getitem__(self, key: int) -> bool:
        return key in self._down


def fire(monkeypatch, control: str, *down: int) -> bool:
    monkeypatch.setattr(pygame.key, "get_pressed", lambda: FakeKeys(*down))
    return KeyboardInputHandler(control).is_fire_pressed()


@pytest.mark.parametrize(
    ("control", "key", "fires"),
    [
        ("R", pygame.K_SPACE, False),  # Space belongs to Player 2 in PVP
        ("R", pygame.K_RCTRL, True),
        ("L", pygame.K_SPACE, True),
        ("L", pygame.K_RCTRL, False),
        ("RL", pygame.K_SPACE, True),
        ("RL", pygame.K_RCTRL, True),
    ],
)
def test_fire_keys_per_control_scheme(monkeypatch, control, key, fires):
    assert fire(monkeypatch, control, key) is fires


@pytest.mark.parametrize("control", ["R", "L", "RL"])
def test_no_keys_means_no_fire(monkeypatch, control):
    assert fire(monkeypatch, control) is False
