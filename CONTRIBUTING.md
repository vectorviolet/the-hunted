# Contributing to The Hunted

How to build, check and change the game. The [README](README.md) is the player-facing front
page, and [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) explains how the code fits together.
`CLAUDE.md` is the same knowledge written for coding agents.

## Setup

Python 3.12+ and [uv](https://docs.astral.sh/uv/) are needed (pygame-ce is resolved from
`pyproject.toml` and `uv.lock`). The engine is a git submodule:

```bash
git clone --recurse-submodules https://github.com/vectorviolet/the-hunted.git
cd the-hunted
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
2. Run `uv run python scripts/gen_credits.py` to regenerate CREDITS.md's asset section and
   `src/credits_data.py` (the credits page's text). Don't edit either by hand.
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
The same workflow builds the Windows installer (`packaging/hunted.iss`, compiled with Inno Setup on
a Windows runner after the Windows zip) and the browser bundle, attaches `hunted-windows-setup.exe`
and `hunted-web.zip` to the release once the desktop release succeeded, and pushes the bundle to the
`html5` channel on itch.io.

### Browser build

`scripts/build_web.py` stages the game and runs [pygbag](https://pypi.org/project/pygbag/) 0.9.3
(pinned, through `uvx`); it needs internet. `web/main.py` is the browser entry point (it awaits
`Game().run_async()`); `web/template.tmpl` is the loading page. Build and serve locally from the
repo root:

```bash
uv run python scripts/build_web.py
python -m http.server 8000 --bind 127.0.0.1 -d build/web
```

Open `http://127.0.0.1:8000` in a focused desktop browser and click the page to start. Use
`127.0.0.1`, not `localhost`: on a `localhost:` URL pygbag assumes its own dev server and fetches
pygame from `/cdn/` on it, which `http.server` doesn't serve (black screen, 404 on the wheel).
`--stage-only` stages the files without pygbag (CI does this). After the first release, enable
**This file will be played in the browser** on the itch.io upload and pick the embed size
(960x540, 16:9, is the game's canvas). Design: [ADR 0001](docs/decisions/0001-web-build.md).

### Windows installer

Build the PyInstaller bundle, then compile the script with [Inno Setup](https://jrsoftware.org/isinfo.php)
(the workflow does this and passes the version from the tag):

```bash
iscc /DAppVersion=0.3.0 packaging/hunted.iss   # writes installer-out/hunted-windows-setup.exe
```

The icon files (`packaging/icon.ico`, `web/icon.png`, `assets/images/icon/icon_64.png`) are made by `scripts/make_icon.py` from a candidate in `scripts/icons/`.
