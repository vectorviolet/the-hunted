# Browser build and Windows installer
<!-- index | refs: #9 | area: Web, packaging -->

**Date:** 2026-11-20 · **Area:** Web, packaging · **Issue:** [#9](https://github.com/vectorviolet/hunted/issues/9) · **ADR:** [0001](../decisions/0001-web-build.md)

## Context

Hunted's releases had desktop zips and itch.io channels only. Highrise and Chokepoint also ship an
itch.io browser build and (Highrise) a Windows installer. Part of bringing Hunted up to the
project standard.

## Decision

Port Highrise's recipe (details in the ADR). What differed:

- Hunted has no saves, config or PyYAML, so the staging is smaller (201 files, 5.4 MB packed).
- The only change to the game is that the browser skips the threaded splash. Everything else ran
  unchanged under pygbag.
- There was no app icon, and the store cover shows Pikachu, a third-party character, so the icon is a
  red "H" on the title card's navy, drawn by `scripts/make_icon.py` with the bundled Comic Neue
  (SIL OFL). The same drawing is the installer's `.ico` and the page's favicon. It is a
  placeholder the owner can swap by replacing `packaging/icon.ico` and `web/icon.png`.
- The loading page shows "THE HUNTED" as text instead of a logo image.
- The installer is Highrise's Inno Setup script with a new AppId, English and Turkish setup
  languages, and no save-data notes.

## Result

Built and played locally in Edge through `python -m http.server`: loader, menu, level select, a
round with keyboard input all work.

![Loading page](img/web-build-loading.png)
![A round in the browser](img/web-build-in-game.png)

The installer itself is built only by the release workflow (Inno Setup on a Windows runner), so
it is first exercised by the next tagged release or a manual workflow run.
