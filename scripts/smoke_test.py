"""Headless boot check -- catches wiring mistakes (missing assets, bad
constant, broken state transition) that only surface once the game is
actually built and run through its states. Run locally with:

    SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run python scripts/smoke_test.py

Requires cwd = repo root (matches how __main__.py and CI both invoke it).
No config files or save data here (this project has neither), so unlike
chokepoint/highrise there's nothing on disk to worry about mutating.
"""
import sys

sys.path.insert(0, "src")
sys.path.insert(0, "src/pygamine")


def boot_game() -> None:
    from game import Game

    game = Game()
    print(f"  {game._state}: OK")

    game.update()
    game.draw()

    game._state = Game.STATE_LEVEL_SELECT
    game.update()
    game.draw()
    print(f"  {game._state}: OK")

    game._enter_game()
    game.update()
    game.draw()
    print(f"  {game._state}: OK")


def run_game_briefly() -> None:
    # The path the steps above never touch: the splash, any run() override
    # and the hand-off into the main loop (a crash there once shipped unseen).
    from game import Game
    from pygamine.devtools.smoke import run_briefly

    frames = run_briefly(Game())
    print(f"  splash + {frames} main-loop frames via the real run(): OK")


def main() -> None:
    print("Booting Game() and cycling every state...")
    boot_game()
    print("Running the real run() -- splash and main loop -- briefly...")
    run_game_briefly()
    print("Smoke test passed.")


if __name__ == "__main__":
    main()
