# Changelog

All notable changes to this project are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project aims to
follow [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- An art style guide (`docs/design/art-style.md`) and the scripts that generate and clean up the art (`scripts/art_gen/`, optional `art` dependency group).
- CREDITS.md (its asset table is generated from `assets/SOURCES.yaml` and lists the assets still waiting for a source or replacement), the asset packs' license texts in `licenses/assets/` (shipped with every build), CONTRIBUTING.md, SECURITY.md, an architecture guide and the devlog and decisions indexes. No change to how the game plays.
- CI runs ruff (lint and format), codespell (American English) and mypy next to the tests. No change to how the game plays.

- Hunted in the browser: the release workflow builds an HTML5 bundle with pygbag, pushes it to the itch.io `html5` channel and attaches `hunted-web.zip` to the GitHub release once the desktop release succeeded; F11 toggles fullscreen and the browser skips the splash screen ([ADR 0001](docs/decisions/0001-web-build.md), [devlog](docs/devlog/2026-11-20-browser-build-and-installer.md)).
- A Windows installer, `hunted-windows-setup.exe` (English or Turkish setup, you pick the folder; Start Menu shortcut, optional desktop shortcut), next to the zips on the GitHub release. The game has an app icon (a vampire face, AI-generated; the owner picked candidate A): the window, the Windows exe, the installer and the browser tab show it.

### Changed

- The repository is now `vectorviolet/the-hunted` (it was `vectorviolet/hunted`): every link, badge and script that named the old URL points at the new one. The game, the build file names (`hunted-windows.zip`, `hunted.exe`, ...) and the itch.io page are unchanged. The README title is a pixel-art wordmark in the title font (`docs/logo.png`, made by `scripts/make_logo.py`) above a row of CI, release, license, coverage and Python badges ([devlog](docs/devlog/2026-11-21-readme-logo.md)). No change to how the game plays.
- README and itch.io store material refreshed: the README shows the new menu flow (PLAY > VS AI / PVP, CREDITS, EXIT), links the browser build and the installer and has new screenshots; `docs/store/` has the edit-page checklist, the page description, three cover candidates (630x500) and a GitHub social preview. `scripts/art_gen/` retakes all the media. No change to how the game plays.
- The main menu is now pages with back buttons: PLAY, CREDITS and EXIT, then a mode menu (VS AI, PVP, BACK) before the countdown and level select, instead of one screen with START and the 1 PLAYER / 2 PLAYER toggles. The credits page is built from `assets/SOURCES.yaml` (by `scripts/gen_credits.py`, into `src/credits_data.py`) and scrolls (mouse wheel or arrow keys). The mode menu, credits and level select have a BACK button, and Esc does the same one page up. EXIT quits on desktop; in the browser build, EXIT and Esc on the main menu open a "Thanks for playing" popup with a link to the itch.io page instead (this fixes Esc freezing the browser page). ([devlog](docs/devlog/2026-11-20-main-menu-pages.md)).

- One consistent pixel-art style for everything (AI-generated with OpenAI Codex, cleaned up to one shared palette): a night background for each level and the menu (the old mountain parallax is gone), new platform and ground art per level, iron menu buttons, panel and level-select card frames, a new cursor, a countdown of pixel glyphs (3, 2, 1, GO, each 15 frames; it replaces the ring and its 0) and a HUD in the palette. The text uses the pixel fonts Jacquard 12 (titles) and Silkscreen (SIL OFL) instead of Comic Neue. The browser loader page uses the same palette. The peasant's bullets are gold with a dark outline so they show on the dark backgrounds. The README screenshots, the preview and the store covers are retaken (the old cover had a third-party character). No change to how the game plays.
- The game is 16:9 now: it draws on a 960x540 canvas (it was 800x600) that pygamine scales with nearest-neighbor, so fullscreen on a 1920x1080 screen is an exact 2x. The backgrounds are 16:9, the platform layouts are stretched to the full width (same vertical steps, so the same jumps), and the menu, level select, countdown and browser page follow. The README screenshots and preview.gif are 1920x1080 frames of it.
- The vampire and the peasant have new pixel-art sprites (AI-generated with OpenAI Codex, then cleaned up with a script) in one shared style. Same 64x64 frames, names and counts, so the animation and hitboxes are unchanged. The old vampire (no known source) and the peasant by Redshrike (CC BY 3.0) are gone, and the unused `peasant/standing.png` was removed.
- The menu music, chase music and jump sound are replaced with CC0 audio (Ogg Vorbis): the two
  CC BY-SA 4.0 tracks by wyver9 and the jump sound of unknown origin are gone. Same places in the game.
- Code style: return types on every function, a few types tightened, and the code reformatted with ruff. No behavior change.
- pygamine updated to 1.0.0+14 (`0049da0`, the commit Chokepoint and Highrise use). No API changes affected Hunted; the game looks and plays the same.
- The unlicensed remove.bg countdown frames (49 PNGs) are gone from the repo; the countdown is now
  drawn from the new glyph art (see the art style entry above).

### Fixed

- Space no longer fires for Player 1 in PVP: the arrow keys player fires with Right Ctrl only, and Space belongs to Player 2 (VS AI still accepts both).

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
