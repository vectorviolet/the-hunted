"""Screenshots of the game (800x600 frames) for the devlog, README and store media.

    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run python scripts/art_gen/shoot.py [prefix]

Writes scripts/art_gen/work/<prefix>_{menu,countdown,level_select,level0,level1,level2}.png
(default prefix "after"). Run from the repo root.
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


def main(prefix: str) -> None:
    import settings
    from entities import Projectile, level_platforms
    from game import Game

    OUT.mkdir(parents=True, exist_ok=True)
    game = Game()

    def save(name: str) -> None:
        game.draw()
        pygame.image.save(game.window, OUT / f"{prefix}_{name}.png")

    game._world.two_players = True
    game.update()
    # The hovered START button (the real cursor is drawn by the engine, not here).
    game._menu.update_button_state("1p", True, False)
    save("menu")
    game._menu.update_button_state("1p", False, False)
    game._countdown = 20
    save("countdown")
    game._countdown = 100

    game._state = Game.STATE_LEVEL_SELECT
    game.mouse.position = game._renderer.level_card_rect(1).center
    save("level_select")

    for i in range(len(settings.LEVELS)):
        game._current_level = i
        game._world.platforms = level_platforms(i)
        game._reset_players()
        game._enter_game()
        plats = game._world.platforms
        # Stand the characters on two platforms; the vampire is the one the game picked.
        for player, plat in ((game._p1, plats[1]), (game._p2, plats[0])):
            player.x = plat.x + plat.width / 2 - 32
            player.y = plat.y - 60
        game._p1.hp = settings.MAX_HP
        game._p2.hp = int(settings.MAX_HP * 0.55)
        game._world.bullets.clear()
        game._world.bullets.append(
            Projectile(
                int(game._p1.x) + 90,
                int(game._p1.y) + 36,
                settings.BULLET_RADIUS,
                settings.BULLET_COLOR,
                1,
            )
        )
        save(f"level{i}")
        game._world.bullets.clear()
        game._state = Game.STATE_LEVEL_SELECT
    print("ok")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "after")
