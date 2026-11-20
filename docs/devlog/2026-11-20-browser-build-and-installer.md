# Browser build and Windows installer
<!-- index | refs: #9, PR #17 | area: Web, packaging -->

**Date:** 2026-11-20 · **Area:** Web, packaging · **Issue:** [#9](https://github.com/vectorviolet/hunted/issues/9) · **PR:** [#17](https://github.com/vectorviolet/hunted/pull/17) · **ADR:** [0001](../decisions/0001-web-build.md)

## Context

Hunted's releases had desktop zips and itch.io channels only. Highrise and Chokepoint also ship an
itch.io browser build and (Highrise) a Windows installer. Part of bringing Hunted up to the
project standard.

## Options

- **Splash in the browser:** keep it (needs threads and a video decode the runtime can't do) or
  skip it. Skipped.
- **Loading logo:** the store cover (4.5 MB, shows Pikachu, a third-party character) or the title
  as text. Text.
- **App icon:** none exists. The cover is out for the same reason; a Kenney cursor is only 32 px.
  A letter drawn from the bundled OFL font is the smallest own work.
- **Build recipe:** write a new one or fork Highrise's, which Chokepoint's also matches. Forked.

## Decision

Port Highrise's recipe (details and the full list of choices in [ADR 0001](../decisions/0001-web-build.md)). What differed:

- Hunted has no saves, config or PyYAML, so the staging is smaller (about 200 files, 5.4 MB packed),
  and CREDITS.md, LICENSE and `licenses/` go into the bundle as in the desktop zips.
- The only change to the game is that the browser skips the threaded splash. Everything else ran
  unchanged under pygbag.
- The icon is a red "H" on the title card's navy, drawn by `scripts/make_icon.py` with Comic Neue
  (SIL OFL). It is the installer's multi-size `.ico` and the page's favicon, and a placeholder the
  owner can swap by replacing `packaging/icon.ico` and `web/icon.png`.
- The installer is Highrise's Inno Setup script with a new AppId, English and Turkish setup
  languages, and no save-data notes.

## Rejected alternatives

- Shipping the store cover as logo or icon: not cleared for redistribution.
- Changing Escape on the menu for the browser (it ends the loop and freezes the page): a design
  decision for the owner, so left as on desktop.

## Result

Built and played locally in Edge through `python -m http.server`: loader, menu, level select, a
round with keyboard input all work.

| Loading page | A round in the browser |
|---|---|
| ![Loading page](img/web-build-loading.png) | ![A round in the browser](img/web-build-in-game.png) |

The installer itself is built only by the release workflow (Inno Setup on a Windows runner), so
it is first exercised by the next tagged release or a manual workflow run.
