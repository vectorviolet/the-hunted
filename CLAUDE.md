# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

Setup, the checks CI runs (pytest, ruff, codespell, mypy, smoke test), the browser build and the
architecture overview are in [CONTRIBUTING.md](CONTRIBUTING.md) and
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md). Only what the code can't tell is below.

## Gotchas

- Unlike its sibling games, the Hunted does **not** use `PanelManager` / `PanelLoaderExt` / YAML
  config. UI is hand-rolled in `src/menu.py` and `src/renderer.py`, and configuration lives in
  `src/settings.py` as plain Python constants.
- `src/pygamine/` is a git submodule shared by six projects: changes there propagate to all of
  them (bump via `scripts/sync-pygamine.bat`).
- Lay out anything new on the 960x540 canvas (`settings.VIRTUAL_W` / `VIRTUAL_H`), never against
  the screen size: `Game` passes `fixed_aspect=True`, so the canvas is scaled
  nearest-neighbor and letterboxed.
- Fonts: `settings.TITLE_FONT` (Jacquard 12, titles only) and `settings.UI_FONT` (Silkscreen,
  everything else). Render them without anti-aliasing and at whole multiples of their pixel grid
  (Silkscreen 16/24/48, Jacquard 12 at 72). Colors drawn in code come from the palette constants
  in `settings.py`. Scenery and UI art is drawn at 2x, characters at 1x
  (`docs/design/art-style.md`).
- The credits text is generated from `assets/SOURCES.yaml` into `src/credits_data.py`; the game
  never reads YAML (the browser build has no PyYAML).
- Keep `PYGBAG_VERSION` in step with the CDN URLs in `web/template.tmpl`.
- Test the browser build on `127.0.0.1`, not `localhost` (pygbag assumes its own dev server on
  `localhost`; see CONTRIBUTING.md).
- The reformat commit is in `.git-blame-ignore-revs`; to hide it in `git blame` run
  `git config blame.ignoreRevsFile .git-blame-ignore-revs` once.

## Assets

Every file under `assets/` must be listed in `assets/SOURCES.yaml` with its source pack (or `own`,
or `unknown` with a `todo`) and its original file name. Each pack needs its license text in
`licenses/assets/<slug>.txt`. CREDITS.md's asset section and `src/credits_data.py` are generated
from `SOURCES.yaml` by `scripts/gen_credits.py`; don't edit them by hand. `tests/test_sources.py`
enforces all of this. Never add an asset whose origin and license you can't state.

## Devlog and ADRs

Every feature or design-decision PR adds or updates an entry in `docs/devlog/`
(`YYYY-MM-DD-short-title.md`); architecture choices get an ADR in `docs/decisions/`
(`NNNN-short-title.md`). Each entry carries an `<!-- index | refs: #N, PR #M -->` comment right
under its heading (see the READMEs' templates). The index tables in both READMEs are generated:
add your entry file, run `uv run python scripts/gen_devlog_index.py`, and never edit the tables by
hand. `tests/test_devlog_index.py` fails in CI if a table is out of date.
