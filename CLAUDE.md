# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the Game

```bash
# Install dependencies (resolved from pyproject.toml / uv.lock)
uv sync             # preferred — installs the locked dep set
# or for users without uv:
pip install .       # installs pygame-ce from pyproject.toml

# Run the game (__main__.py adds src/ and src/pygamine/ to sys.path)
python __main__.py
```

## Testing

```bash
uv run --group dev pytest tests/ -q                      # this app's own logic tests
uv run --group dev pytest tests/ --cov --cov-report=term  # with coverage
```

`tests/conftest.py` runs pygame headless (`SDL_VIDEODRIVER=dummy`).

## Lint, Format, Spelling and Types

Same setup as highrise (config in `pyproject.toml`; the pygamine submodule has its own and is skipped). CI runs all of these:

```bash
uv run --group dev ruff check .          # lint: pyflakes, return types, complexity caps
uv run --group dev ruff format .         # format (CI uses `ruff format --check .`)
uv run --group dev codespell             # typos + American English (.codespell-en-us.txt)
uv run --group dev mypy                  # lenient start: src/ only, untyped functions skipped
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run python scripts/smoke_test.py   # headless boot
```

The reformat commit is listed in `.git-blame-ignore-revs`; to hide it in `git blame` run
`git config blame.ignoreRevsFile .git-blame-ignore-revs` once.

## Architecture Overview

### Entry Point and Game Class

`__main__.py` injects `src/` and `src/pygamine/` into `sys.path`, then calls `Game().run()`. `src/game.py` defines `Game`, which inherits from `pygamine.Application`.

Unlike its sibling games that use the YAML-driven panel system (`chokepoint`, `highrise`, `standoff`, `terraria`), the Hunted does **not** use `PanelManager` / `PanelLoaderExt` / YAML config — UI is hand-rolled in `src/menu.py` and `src/renderer.py`, and configuration lives in `src/settings.py` as plain Python constants (`artifical-chaos` opts out the same way).

### pygamine — Shared Submodule

`src/pygamine/` is a git submodule pointing at `https://github.com/vectorviolet/pygamine.git`. The same submodule is used by `chokepoint`, `highrise`, `standoff`, `terraria`, and `artifical-chaos`. Changes here propagate to all six projects — bump via `scripts/sync-pygamine.bat`.

This project uses only a small slice of pygamine: `Application`, `Mouse`, and `GameObject` (for `Cursor`).

### Game State Machine

`Game` dispatches on `self._state`, which takes one of three string constants:

| State | Driven by | Drawn by |
|-------|-----------|----------|
| `STATE_MENU` | `_handle_menu_event` / `_update_menu` | `Menu.draw()` |
| `STATE_LEVEL_SELECT` | `_handle_level_select_event` / `_update_level_select` | `GameRenderer.draw_level_select()` |
| `STATE_GAME` | `_update_game` (no event handler — input is polled in `Player`) | `GameRenderer.draw_game()` |

State transitions happen in-band inside the handlers (e.g. `_update_menu` flips to `STATE_LEVEL_SELECT` after a countdown).

### Subsystems (composed in `Game.__init__`)

| Attribute | Class | Responsibility |
|-----------|-------|----------------|
| `_world` | `GameWorld` (dataclass, `src/world.py`) | Window size, platforms list, bullets list, `two_players` flag |
| `_menu` | `Menu` (`src/menu.py`) | Main-menu buttons + countdown (drawn by `src/countdown.py`) + button-state visuals |
| `_audio` | `AudioManager` (`src/audio.py`) | Two music tracks (menu / game) on the default mixer |
| `_renderer` | `GameRenderer` (`src/renderer.py`) | Level-select and in-game drawing |
| `_combat` | `CombatSystem` (`src/combat.py`) | Bullet physics, contact damage, round transitions |
| `_cursor` | `Cursor` (`src/cursor.py`, extends `pygamine.GameObject`) | Custom mouse cursor (one static image per state; switch with `set_state`) |

### Players and Input

`Player` (`src/entities.py`) has two roles toggled by `be_vampire()` / `be_peasant()` (loads different sprite sets + speed). `CombatSystem.begin_round()` randomly assigns vampire on each new round.

Input is dispatched through `InputHandler` (Protocol in `src/input_handler.py`):
- `KeyboardInputHandler(control)` where `control` is `"L"` (WASD + Space), `"R"` (Arrows + RCtrl), or `"RL"` (both keysets, used in 1-player mode).
- `AIInputHandler` drives the opponent in 1-player mode. It has separate vampire/peasant strategies and reads opponent position + platform layout to decide moves.

### Levels

`settings.LEVELS` defines three platform layouts (`Classic`, `Towers`, `Arena`). Level selection happens on `STATE_LEVEL_SELECT`; `_handle_level_select_event` rebuilds `_world.platforms` from `LEVELS[i]['platforms']` before entering the game.

### Assets

All images, sounds and the font live under `assets/`. Loaded directly with `pygame.image.load()` / `pygame.mixer.Sound()` — there is no asset loader in code. Naming conventions:
- `assets/images/vampire/R{i}E.png`, `L{i}E.png` for vampire walk frames (1-9)
- `assets/images/peasant/R{i}.png`, `L{i}.png` for peasant walk frames
- `assets/images/cursor/*.png` and `assets/images/buttons/*.png` are Kenney CC0 images (see `assets/SOURCES.yaml`); `Cursor` shows one static image per state, `src/buttons.py` draws the menu buttons from them and the labels in the game font

**Asset sources:** every file under `assets/` must be listed in `assets/SOURCES.yaml` with its
source pack (or `own`, or `unknown` with a `todo`) and its original file name. Each pack needs its
license text in `licenses/assets/<slug>.txt`. CREDITS.md's asset section is generated from
`SOURCES.yaml` by `scripts/gen_credits.py`; don't edit it by hand. `tests/test_sources.py` enforces
all of this. Never add an asset whose origin and license you can't state.

**Devlog and ADRs:** every feature or design-decision PR adds or updates an entry in
`docs/devlog/` (`YYYY-MM-DD-short-title.md`); architecture choices get an ADR in
`docs/decisions/` (`NNNN-short-title.md`). Each entry carries an `<!-- index | refs: #N, PR #M -->`
comment right under its heading (see the READMEs' templates). The index tables in both READMEs are
generated: add your entry file, run `uv run python scripts/gen_devlog_index.py`, and never edit
the tables by hand. `tests/test_devlog_index.py` fails in CI if a table is out of date.
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) is the human-facing version of this overview.

### Persistence

None. Scores and round state are kept in memory only.

### What's missing relative to the modern sibling projects

This project predates the YAML-driven layout, the `app/domain/gameplay/ui` package split, and `pygamine.AssetManager`. If extending significantly, consider porting it onto those patterns (see `chokepoint` / `highrise` / `standoff` / `terraria` for examples).
