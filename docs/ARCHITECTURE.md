# Architecture

A guided tour of how The Hunted is put together, for people reading or changing the code. It is
deliberately high level: the code and its docstrings have the details, and
[`docs/decisions/`](decisions/README.md) records why the bigger choices were made. For how to build
and check changes, see [CONTRIBUTING.md](../CONTRIBUTING.md). (`CLAUDE.md` is the agent-facing
version of this tour.)

## Project layout

```
__main__.py            Entry point: puts src/ and src/pygamine/ on sys.path, runs Game
src/game.py            Game: the state machine over menu / level select / game
src/world.py           GameWorld dataclass (window size, platforms, bullets, two_players)
src/entities.py        Player, Platform, Projectile
src/combat.py          CombatSystem: bullet physics, contact damage, round transitions
src/input_handler.py   InputHandler protocol, KeyboardInputHandler, AIInputHandler
src/menu.py            Main-menu buttons and their button-state visuals
src/countdown.py       The pre-game countdown (3, 2, 1, GO) from the glyph art
src/renderer.py        Level-select and in-game drawing
src/background.py      load_background: the full-screen picture of a level or the menu
src/pixelart.py        three_slice and nine_slice: platform strips and UI frames at any size
src/buttons.py         Menu button images (iron art + the label in the UI font)
src/audio.py           Menu and game music
src/cursor.py          Custom multi-state mouse cursor
src/settings.py        Canvas size (960x540), physics, combat, colors and the three level layouts, as plain constants
src/util/              Frozen-build resource paths, the browser check (web.py)
src/pygamine/          Engine submodule (Application, Mouse and GameObject are used)
assets/                Images, sounds, fonts (every file listed in assets/SOURCES.yaml)
licenses/              License texts of the asset packs (the software's come with pygamine)
scripts/               Smoke test, credits and devlog generators, web build, icon, submodule sync
web/                   Browser build (pygbag): entry point, loader page, icon
packaging/             Windows installer script (Inno Setup) and icon
tests/                 The app's own pytest suite
docs/                  Devlog, decision records, screenshots, store art
```

The game is built on [pygamine](https://github.com/vectorviolet/pygamine), the author's own engine
layer on top of pygame-ce, pinned as a git submodule in `src/pygamine/`. The same submodule is used
by the other VectorViolet games, so a change there affects all of them. The Hunted only uses a
small slice of it: `Application`, `Mouse` and `GameObject` (for `Cursor`).

Unlike its sibling games, The Hunted predates the YAML-driven panel system: its UI is hand-rolled
in `src/menu.py` and `src/renderer.py`, and its configuration is plain Python constants in
`src/settings.py`.

## Entry point and the Game class

`__main__.py` creates `Game()` and calls `run()`. `Game` (`src/game.py`) extends
`pygamine.Application`, creates the subsystems below and dispatches on `self._state`, one of three
string constants:

| State | Driven by | Drawn by |
|---|---|---|
| `STATE_MENU` | `_handle_menu_event` / `_update_menu` | `Menu.draw()` |
| `STATE_LEVEL_SELECT` | `_handle_level_select_event` / `_update_level_select` | `GameRenderer.draw_level_select()` |
| `STATE_GAME` | `_update_game` (no event handler: input is polled in `Player`) | `GameRenderer.draw_game()` |

State changes happen inside the handlers; for example `_update_menu` moves to level select when
the countdown ends.

## Subsystems

| Attribute on `Game` | Class | Responsibility |
|---|---|---|
| `_world` | `GameWorld` | Window size, platforms, bullets, the `two_players` flag |
| `_menu` | `Menu` | Main-menu buttons, the countdown and the button-state visuals |
| `_audio` | `AudioManager` | Two music tracks (menu and game) on the default mixer |
| `_renderer` | `GameRenderer` | Level-select and in-game drawing |
| `_combat` | `CombatSystem` | Bullet physics, contact damage, round transitions |
| `_cursor` | `Cursor` | The custom mouse cursor (normal, click, click2, help and writing states) |

## Players, roles and input

A `Player` has two roles, switched by `be_vampire()` and `be_peasant()`, which load different sprite
sets and speeds. The vampire is faster and wins by touching the peasant; only the peasant fires.
`CombatSystem.begin_round()` assigns the vampire at random each round.

Input goes through the `InputHandler` protocol (`src/input_handler.py`):

- `KeyboardInputHandler(control)`, where `control` is `"L"` (WASD and Space), `"R"` (arrows and
  right Ctrl) or `"RL"` (both sets, used in one-player mode).
- `AIInputHandler` drives the opponent in one-player mode, with separate vampire and peasant
  strategies; it reads the opponent's position and the platform layout to decide its moves.

## Levels

`settings.LEVELS` defines three platform layouts (Classic, Towers and Arena). On the level-select
screen, `_handle_level_select_event` rebuilds `_world.platforms` from the chosen level before the
game starts.

## Assets and credits

Images, sounds and the font live under `assets/` and are loaded by relative path with
`pygame.image.load()` and `pygame.mixer.Sound()`; there is no loader or asset manifest in code. In
a PyInstaller bundle, `__main__` changes into `util.paths.resource_root()` first so the same
relative paths resolve.

`assets/SOURCES.yaml` is the manifest of where each file comes from (pack, `own`, or `unknown` with
a `todo`). `scripts/gen_credits.py` builds CREDITS.md's asset section from it, and
`tests/test_sources.py` fails when the file list, the license texts in `licenses/assets/` or
CREDITS.md drift from it.

## Persistence

None. Scores and round state stay in memory.

## Tests and checks

`tests/` holds the app's own logic tests (physics, combat, AI, menu, renderer, cursor, countdown,
asset sources, devlog index); `tests/conftest.py` runs pygame headless. `scripts/smoke_test.py`
boots the real `Game().run()` headless. CI also runs ruff, codespell and mypy; the commands are in
[CONTRIBUTING.md](../CONTRIBUTING.md).
