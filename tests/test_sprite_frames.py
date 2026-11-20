"""The vampire and peasant walk frames fit the unchanged hitboxes in entities.Player:
64x64, hard alpha, feet on one baseline, and the art centered on the hitbox."""

from __future__ import annotations

import pygame
import pytest

from entities import Player

CASES = [("vampire", "E", "vampire"), ("peasant", "", "peasant")]
FRAMES = [(d, i) for d in "LR" for i in range(1, 10)]


def _load(folder: str, suffix: str, d: str, i: int) -> pygame.Surface:
    return pygame.image.load(f"assets/images/{folder}/{d}{i}{suffix}.png")


@pytest.mark.parametrize(("folder", "suffix", "role"), CASES)
def test_frames_are_64px_with_hard_alpha_on_one_baseline(folder, suffix, role):
    bottoms = set()
    for d, i in FRAMES:
        img = _load(folder, suffix, d, i)
        assert img.get_size() == (64, 64)
        alphas = {img.get_at((x, y)).a for x in range(64) for y in range(64)}
        assert alphas == {0, 255}, (d, i)
        bottoms.add(img.get_bounding_rect().bottom)
    assert len(bottoms) == 1


@pytest.mark.parametrize(("folder", "suffix", "role"), CASES)
def test_frames_are_centered_on_the_hitbox(folder, suffix, role):
    ox, _, w, _ = Player._HITBOX[role]
    hitbox_center = ox + w / 2
    for d, i in FRAMES:
        box = _load(folder, suffix, d, i).get_bounding_rect()
        # a trailing cape or a long stride moves the frame's center a few px, not more
        assert abs(box.centerx - hitbox_center) <= 4, (d, i, box)


@pytest.mark.parametrize(("folder", "suffix", "role"), CASES)
def test_every_edge_pixel_is_the_light_outline(folder, suffix, role):
    for d, i in FRAMES:
        img = _load(folder, suffix, d, i)
        for x in range(64):
            for y in range(64):
                if img.get_at((x, y)).a == 0:
                    continue
                around = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
                if any(
                    not (0 <= nx < 64 and 0 <= ny < 64) or img.get_at((nx, ny)).a == 0
                    for nx, ny in around
                ):
                    assert tuple(img.get_at((x, y)))[:3] == (255, 244, 214), (
                        d,
                        i,
                        x,
                        y,
                    )
