# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project aims to
follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- CREDITS.md (its asset table is generated from `assets/SOURCES.yaml` and lists the assets still waiting for a source or replacement), the asset packs' license texts in `licenses/assets/` (shipped with every build), CONTRIBUTING.md, SECURITY.md, an architecture guide and the devlog and decisions indexes. No change to how the game plays.
- CI runs ruff (lint and format), codespell (American English) and mypy next to the tests. No change to how the game plays.

- Hunted in the browser: the release workflow builds an HTML5 bundle with pygbag, pushes it to the itch.io `html5` channel and attaches `hunted-web.zip` to the GitHub release once the desktop release succeeded; F11 toggles fullscreen and the browser skips the splash screen ([ADR 0001](docs/decisions/0001-web-build.md), [devlog](docs/devlog/2026-11-20-browser-build-and-installer.md)).
- A Windows installer, `hunted-windows-setup.exe` (English or Turkish setup, you pick the folder; Start Menu shortcut, optional desktop shortcut), next to the zips on the GitHub release. The game has an app icon (a vampire face, AI-generated, pending the owner's choice among three candidates): the window, the Windows exe, the installer and the browser tab show it.

### Changed

- The menu buttons and the mouse cursor use Kenney CC0 art (UI Pack and Cursor Pack) instead of images with no known license. The buttons keep their positions, sizes and hover/pressed states, with the labels drawn in the game font; the cursor is now one static image per state instead of animated frames.
- The menu music, chase music and jump sound are replaced with CC0 audio (Ogg Vorbis): the two
  CC BY-SA 4.0 tracks by wyver9 and the jump sound of unknown origin are gone. Same places in the game.
- Code style: return types on every function, a few types tightened, and the code reformatted with ruff. No behavior change.
- pygamine updated to 1.0.0+14 (`0049da0`, the commit Chokepoint and Highrise use). No API changes affected Hunted; the game looks and plays the same.
- The pre-game countdown (3, 2, 1, 0, GO) is drawn in code instead of playing 49 PNG frames, so
  the unlicensed remove.bg frames are gone from the repo. Same look and timing.

## [0.2.1] – 2026-10-24

### Added

- Tests for the modules that had no coverage.

### Changed

- Text uses the bundled Comic Neue (SIL OFL) instead of the system Comic Sans, so the game looks the
  same on every machine; sizes are scaled to keep the layout.
- Startup now opens with the shared splash all the sibling games use: the publisher clip, then
  the pygame logo.
- pygamine updated to 0.19.0, now at `vectorviolet/pygamine`; repo links point at `vectorviolet`.
- The smoke test now runs the game's real `run()`, splash included, instead of stepping frames by hand.

## [0.2.0] – 2026-08-12

### Added

- Startup splash screen.
- CI workflow running `pygamine`'s test suite, a real app-level test suite covering physics, combat
  and AI, and an app-level smoke test that boots `Game()` and cycles every state.
- itch.io/storefront cover art.

### Changed

- Replaced unlicensed music with CC BY-SA 4.0 tracks by wyver9, and unlicensed background/platform
  art with CC0 parallax background and tiled ground.
- Renamed the `pygame_core` submodule/dependency to `pygamine`.
- Converged `pygame_core` with sibling projects; letterboxing now lives in Hunted itself.

### Fixed

- Editable `pygame-core` install not actually taking effect.
- Stale sibling-project references in `CLAUDE.md`.

## [0.1.0] – 2026-07-07

Initial release. Renamed from an earlier prototype ("start") to The Hunted, migrated onto
`pygame_core` with a single-player AI opponent mode, PyInstaller build/release automation, and
itch.io publishing.
