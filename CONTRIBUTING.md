# Contributing to The Hunted

How to build, check and change the game. The [README](README.md) is the player-facing front
page, and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) explains how the code fits together.
`CLAUDE.md` is the same knowledge written for coding agents.

## Setup

Python 3.12+ and [uv](https://docs.astral.sh/uv/) are needed (pygame-ce is resolved from
`pyproject.toml` and `uv.lock`). The engine is a git submodule:

```bash
git clone --recurse-submodules https://github.com/vectorviolet/hunted.git
cd hunted
uv sync
uv run python __main__.py
```

In a fresh worktree or after a pull that moves the engine, run `git submodule update --init`
(on Windows, `scripts\sync-pygamine.bat` does the same).

## Checks

Run these from the project folder before every commit; CI runs the same:

```bash
uv run --group dev pytest tests/ -q                       # the app's own tests
uv run --group dev pytest tests/ --cov --cov-report=term  # with coverage
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run python scripts/smoke_test.py  # boots the game headless
uv run --group dev ruff format --check .                  # formatting (drop --check to reformat)
uv run --group dev ruff check .                           # lint
uv run --group dev mypy                                   # types (lenient, src/ only)
uv run --group dev codespell                              # typos, American English
```

### Code style

- **Formatting:** Black-compatible, enforced by `ruff format` (line length 88, double quotes).
- **Lint:** `ruff check`: pyflakes, a return type on every function in `src/`, no-self-use and
  complexity limits (see `[tool.ruff.lint]` in `pyproject.toml`).
- **Spelling:** American English everywhere (code, docs, comments). Real words that codespell
  flags go in `ignore-words-list` in `pyproject.toml`, with a reason.
- The `src/pygamine` submodule is excluded from all of these; it has its own setup and CI.
- The commit that first applied the formatter is in `.git-blame-ignore-revs`. To have `git blame`
  skip it: `git config blame.ignoreRevsFile .git-blame-ignore-revs`.

## Asset sources

Every file under `assets/` is listed in `assets/SOURCES.yaml` with its source: a pack (given by
its slug, plus the file's path inside the pack as `original`), `own` for files made for this game,
or `unknown` with a `todo` saying what is left to do. The `packs` section names each pack, its
author, URL, license and what the game uses it for. Each pack's own license text is in
`licenses/assets/<slug>.txt`, and every build ships it.

When you add, replace or remove an asset:

1. Update `assets/SOURCES.yaml`, and add `licenses/assets/<slug>.txt` for any new pack.
2. Run `uv run python scripts/gen_credits.py` to regenerate CREDITS.md's asset section. Don't edit
   that section by hand.
3. Run the tests. `tests/test_sources.py` fails if a file is missing from `SOURCES.yaml`, if a
   listed file doesn't exist, if a pack has no license text, or if CREDITS.md is out of date.

Only add assets whose license allows bundling them in a distributed game (CC0, CC BY or OFL).
Never add an asset whose origin and license you can't state.

## Pull requests, devlog and ADRs

1. Fork, clone with `--recurse-submodules`, and create a branch (`feature/<name>`).
2. Run the checks above. Stage the files you changed by explicit path.
3. Open a pull request. The title is a conventional prefix and a plain description (for example
   "fix: The AI no longer walks off the level"), without an issue number; link the issue in the
   body with "Closes #N".
4. A feature or design-decision PR adds or updates an entry in [`docs/devlog/`](docs/devlog/README.md)
   (`YYYY-MM-DD-short-title.md`: context, options with screenshots, decision, rejected, result);
   an architecture choice gets an ADR in [`docs/decisions/`](docs/decisions/README.md). Add the file,
   then run `uv run python scripts/gen_devlog_index.py` to rebuild the index tables (never edit them
   by hand; `tests/test_devlog_index.py` fails when they are stale). Add a line to
   [CHANGELOG.md](CHANGELOG.md) for what players see.
5. `main` is protected: changes land through a pull request whose required checks pass.

## Building a standalone bundle

[PyInstaller](https://pyinstaller.org/) builds it from `hunted.spec`, which bundles `assets/` and
the license texts next to the executable (onedir):

```bash
uv sync --group build
uv run pyinstaller hunted.spec --noconfirm
```

The result lands in `dist/hunted/` (`dist/Hunted.app` on macOS).

### Cutting a release

A release goes through a "Release x.y.z" PR (version and changelog), then the owner tags the merged
commit `vx.y.z`. The tag triggers [`.github/workflows/release.yml`](.github/workflows/release.yml),
which builds each OS, attaches the zips to a GitHub release (with auto-generated notes) and pushes
each build to its [itch.io](https://umutcanekinci.itch.io/the-hunted) channel with
[Butler](https://itch.io/docs/butler/). **Run workflow** builds without publishing.
