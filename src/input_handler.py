from __future__ import annotations

import random
from typing import TYPE_CHECKING, Protocol, runtime_checkable

import pygame

if TYPE_CHECKING:
    from entities import Player


@runtime_checkable
class InputHandler(Protocol):
    control: str

    def is_moving_right(self) -> bool: ...
    def is_moving_left(self) -> bool: ...
    def is_jump_pressed(self) -> bool: ...
    def is_fire_pressed(self) -> bool: ...


class KeyboardInputHandler:
    def __init__(self, control: str) -> None:
        self.control = control

    def is_moving_right(self) -> bool:
        keys = pygame.key.get_pressed()
        return (
            (self.control in ("R", "RL") and keys[pygame.K_RIGHT]) or
            (self.control in ("L", "RL") and keys[ord('d')])
        )

    def is_moving_left(self) -> bool:
        keys = pygame.key.get_pressed()
        return (
            (self.control in ("R", "RL") and keys[pygame.K_LEFT]) or
            (self.control in ("L", "RL") and keys[ord('a')])
        )

    def is_jump_pressed(self) -> bool:
        keys = pygame.key.get_pressed()
        return (
            (self.control in ("R", "RL") and keys[pygame.K_UP]) or
            (self.control in ("L", "RL") and keys[pygame.K_w])
        )

    def is_fire_pressed(self) -> bool:
        keys = pygame.key.get_pressed()
        arrows = self.control in ("R", "RL")
        wasd   = self.control in ("L", "RL")
        return (
            (arrows and (keys[pygame.K_RCTRL] or keys[pygame.K_SPACE])) or
            (wasd   and  keys[pygame.K_SPACE])
        )


class AIInputHandler:
    """Drives a Player by reading its own state, the opponent's, and the world."""

    def __init__(self) -> None:
        self.control = "AI"
        self._bound_self: Player | None = None
        self._bound_target: Player | None = None

    @property
    def _self(self) -> Player:
        # Only read after _ready() has confirmed bind() ran.
        assert self._bound_self is not None
        return self._bound_self

    @property
    def _target(self) -> Player:
        assert self._bound_target is not None
        return self._bound_target

    def bind(self, self_player: Player, target_player: Player) -> None:
        self._bound_self = self_player
        self._bound_target = target_player

    def _ready(self) -> bool:
        return self._bound_self is not None and self._bound_target is not None

    def _dx(self) -> float:
        # Wrap-aware horizontal delta (chase the short way around the screen).
        raw = self._target.x - self._self.x
        w = self._self._world.window_w
        if raw > w / 2:
            return raw - w
        if raw < -w / 2:
            return raw + w
        return raw

    def _dy(self) -> float:
        return self._target.y - self._self.y

    def is_moving_right(self) -> bool:
        if not self._ready():
            return False
        dx = self._dx()
        if self._self.vampire:
            return dx > 4
        abs_dx = abs(dx)
        facing_target = (self._self.left and dx < 0) or (not self._self.left and dx > 0)
        if abs_dx < 80:
            return dx < 0  # too close: retreat
        if abs_dx > 180:
            return dx > 0  # too far: close in
        if not facing_target:
            return dx > 0  # in range but facing wrong way: turn
        return False

    def is_moving_left(self) -> bool:
        if not self._ready():
            return False
        dx = self._dx()
        if self._self.vampire:
            return dx < -4
        abs_dx = abs(dx)
        facing_target = (self._self.left and dx < 0) or (not self._self.left and dx > 0)
        if abs_dx < 80:
            return dx > 0
        if abs_dx > 180:
            return dx < 0
        if not facing_target:
            return dx < 0
        return False

    def is_jump_pressed(self) -> bool:
        if not self._ready() or not self._self.on_ground:
            return False
        dy = self._dy()
        if self._self.vampire:
            if dy < -40:
                return random.random() < 0.45  # chase upward
            if self._platform_in_chase_path():
                return random.random() < 0.3   # leap onto intermediate platform
            return random.random() < 0.01
        # peasant
        dx = self._dx()
        if abs(dx) < 90 and abs(dy) < 60:
            return random.random() < 0.6       # vampire is close — bail out
        if self._platform_above_self():
            return random.random() < 0.12      # take the high ground
        return random.random() < 0.005

    def is_fire_pressed(self) -> bool:
        if not self._ready() or self._self.vampire:
            return False
        if abs(self._dy()) > 70:
            return False
        dx = self._dx()
        if self._self.left and dx < -12:
            return True
        if not self._self.left and dx > 12:
            return True
        return False

    def _platform_in_chase_path(self) -> bool:
        """Vampire: is there a platform between us and the target worth leaping onto?"""
        dx = self._dx()
        my_x, my_y = self._self.x, self._self.y
        target_x = my_x + dx
        for plat in self._self._world.platforms:
            plat_mid = plat.x + plat.width / 2
            in_chase = (
                (dx > 0 and my_x < plat_mid < target_x) or
                (dx < 0 and target_x < plat_mid < my_x)
            )
            if in_chase and 20 < my_y - plat.y < 180:
                return True
        return False

    def _platform_above_self(self) -> bool:
        """Peasant: is there a platform directly above we could jump onto?"""
        my_x, my_y = self._self.x, self._self.y
        for plat in self._self._world.platforms:
            if 30 < my_y - plat.y < 160:
                if plat.x - 20 <= my_x <= plat.x + plat.width + 20:
                    return True
        return False