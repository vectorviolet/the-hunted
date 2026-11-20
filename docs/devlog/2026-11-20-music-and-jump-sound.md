# Replacing the music and the jump sound
<!-- index | refs: #7, PR #15 -->

**Date:** 2026-11-20 · **Area:** Audio · **PR:** [#15](https://github.com/vectorviolet/the-hunted/pull/15)

## Context

Both music tracks (`menu_theme.wav`, `chase_theme.wav`) came from wyver9's "8-Bit Beat'em Up
Soundtrack", licensed CC BY-SA 4.0. ShareAlike is a gray area for a game: it is unclear whether it
would reach the game itself or only the audio files, and it is outside the licenses Hunted
accepts (CC0, CC BY, OFL). `jump.wav` had no recorded source at all. The owner decided on
2026-11-20 to replace all three with CC0 or CC BY audio.

## Options

All pages were checked for the license on the page itself. Anything BY-SA, NonCommercial or NoDerivatives was excluded
(for example wyver9's "Funny Chase" and "Fast Level" are CC BY-SA 3.0).

### Menu music (calm, moody 8-bit loop)

| Track | Author | License | Why |
|---|---|---|---|
| [forgotten path](https://opengameart.org/content/forgotten-path) (first pick) | johndekale | CC0 | Melancholic chiptune loop, 40 s, ships as .ogg |
| [8-bit - Truth](https://opengameart.org/content/8-bit-truth) (final pick) | HydroGene | CC0 | Calm, sad NES-style theme that loops seamlessly, 111 s (MP3) |
| [Lonely Night](https://opengameart.org/content/lonely-night) | Centurion_of_war | CC0 | Small, slight calm tune, 64 s, ships as .ogg |

### Chase music (tense, fast 8-bit loop)

| Track | Author | License | Why |
|---|---|---|---|
| [8-bit Epic Space Shooter Music](https://opengameart.org/content/8-bit-epic-space-shooter-music) (picked) | HydroGene | CC0 | Driving action chiptune that loops seamlessly, 82 s, loud like the old track |
| [Chip Bit Danger](https://opengameart.org/content/chip-bit-danger) | Sudocolon | CC0 | "Actiony chiptune loop", 59 s (MP3) |
| [Vigour (decisive chiptune theme, 8bit)](https://opengameart.org/content/vigour-decisive-chiptune-theme-8bit) | wyver9 | CC BY 3.0 / 4.0 | Same artist as before but a different license, tagged for beat'em ups; needs credit, 60 s |

[8-Bit Battle Loop](https://opengameart.org/content/8-bit-battle-loop) by Wolfgang_ (CC0) was
dropped: it is only 27 s and very quiet.

### Jump sound

Kenney's Interface Sounds (CC0) are already in the asset library. The old jump sound rises from
about 290 Hz to 650 Hz over 0.6 s. `maximize_006.ogg` rises from about 280 Hz to 610 Hz over 0.4 s
at a similar level, which was the closest match among the pack's sounds.

## Decision

- Menu: "8-bit - Truth" (owner's pick after listening). My first pick was "forgotten path", for
  the mood and because it was already an .ogg; the owner preferred Truth.
- Chase: "8-bit Epic Space Shooter Music", because it loops seamlessly and has the pace of a chase.
- Jump: `maximize_006.ogg` from Kenney's Interface Sounds.

Rejected: keeping the wyver9 tracks with attribution and a ShareAlike notice (the gray area),
and Vigour for the chase (CC BY is allowed, but it adds a credit and a second license).

## Result

- Files are Ogg Vorbis: `assets/sounds/menu_theme.ogg`, `chase_theme.ogg`, `jump.ogg`. The
  repo is about 17 MB smaller because the old WAVs are gone.
- Both music tracks were converted from MP3 without a volume change; they average about -15 dB,
  against -11 dB for the old tracks.
- No code changes beyond the three file names in `src/audio.py` and `src/entities.py`.
- The WAVs are still in git history, so the wyver9 audio remains downloadable from old commits.
