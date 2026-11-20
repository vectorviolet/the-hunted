# 0001. Browser build using Highrise's pygbag recipe
<!-- index | refs: #9 -->

- **Status:** Proposed
- **Date:** 2026-11-20
- **Issues / PRs:** [#9](https://github.com/vectorviolet/hunted/issues/9)

## Context

Highrise and Chokepoint already run in desktop browsers through pygbag 0.9.3
([Highrise ADR 0004](https://github.com/vectorviolet/highrise/blob/main/docs/decisions/0004-web-build.md)).
Hunted uses the same pygamine commit, which has `Application.run_async()`. Hunted is simpler than
those games: no saves, no config files, no PyYAML, one 800x600 canvas, and its logic runs per
frame at 60 FPS, the same as the browser's frame rate, so no catch-up stepping is needed.

## Decision

- **Build:** `scripts/build_web.py` stages `web/main.py` as `main.py`, `src/`, pygamine's package
  (without its splash clip) and `assets/`, then runs the pinned pygbag (`PYGBAG_VERSION`, run
  through `uvx`). It is a fork of Highrise's script minus the YAML vendoring, `config/` and logo;
  a fix to one should be checked against the other.
- **Loop:** `web/main.py` awaits `Game().run_async()`; the desktop entry point stays
  `__main__.py` and `Game.run()`. A start-up failure is shown on the page instead of a blank canvas.
- **Splash:** the splash decodes video frames on a thread, which the browser lacks, so `Game` sets
  no splash when `util.web.is_web()` (`sys.platform == "emscripten"`). `util/web.py` holds only that
  check; there is nothing else browser-specific to wrap.
- **Page:** `web/template.tmpl` is Highrise's loader page (click to play, so the music may start)
  with the title drawn as text instead of a logo image, and `web/icon.png` as favicon and pygbag
  icon. The store cover art is not shipped in the bundle.
- **Release:** `release.yml` gets `web` (build, check itch.io's HTML5 limits, zip),
  `publish-web` (the `html5` channel of the same itch.io game as the desktop builds) and
  `attach-web` (after the desktop release succeeded). CI stages the bundle without pygbag
  (`web-stage`). The desktop `release` and `publish-itch` jobs now download only `hunted-*`
  artifacts, so the web zip and the installer are not attached twice.

## Consequences

- The browser build needs internet at build time (pygbag fetches its runtime) and at play time
  (the runtime loads from pygame-web.github.io).
- A failed web build never blocks the desktop release.
- `tests/test_build_web.py` and `tests/test_web_release.py` check the stage contents, the pygbag
  call, the template's hooks and contrast, and which events may publish.
- Escape on the menu still ends the game loop, as on desktop; in the browser this leaves a frozen
  page until reload. Not changed here (no gameplay changes).

## Alternatives considered

- **Keeping the splash in the browser:** it needs threads and a video decode the runtime can't do.
- **Shipping the store cover as the loading logo:** it is 4.5 MB and shows Pikachu, a third-party
  character, so it is not for redistribution.
