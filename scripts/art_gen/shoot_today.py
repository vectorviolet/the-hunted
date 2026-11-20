"""Save screenshots of the game as it is today (current main), for the art mockups.

    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run python scripts/art_gen/shoot_today.py

Writes scripts/art_gen/work/today_{menu,level_select,level0,level1,level2}.png (800x600).
Run from the repo root.
"""

import os
import sys
from pathlib import Path

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
sys.path.insert(0, "src")
sys.path.insert(0, "src/pygamine")

import pygame  # noqa: E402

OUT = Path("scripts/art_gen/work")


def main() -> None:
    import settings
    from entities import Platform
    from game import Game

    OUT.mkdir(parents=True, exist_ok=True)
    game = Game()
    game.update()
    game.draw()
    pygame.image.save(game.window, OUT / "today_menu.png")

    game._state = Game.STATE_LEVEL_SELECT
    game.update()
    game.draw()
    pygame.image.save(game.window, OUT / "today_level_select.png")

    for i, level in enumerate(settings.LEVELS):
        game._current_level = i
        game._world.platforms = [
            Platform(loc, w, h) for loc, w, h in level["platforms"]
        ]
        game._enter_game()
        game._p1.x, game._p1.y = 120.0, settings.FLOOR_Y
        game._p2.x, game._p2.y = 600.0, settings.FLOOR_Y
        game.update()
        game.draw()
        pygame.image.save(game.window, OUT / f"today_level{i}.png")
        game._state = Game.STATE_LEVEL_SELECT
    print("ok")


if __name__ == "__main__":
    main()
