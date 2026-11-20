# Hunted art style guide

Status: proposal for the owner's pick (issue #19, phase 1). Nothing here is wired into the game
yet. The anchors are the new characters (`assets/images/vampire/`, `assets/images/peasant/`, PR #16)
and icon A (PR #17). The one rule above all others: **everything looks like it was drawn by the
same hand as the characters.**

![Palette](../devlog/img/19-palette.png)

## Palette

One shared palette of 63 colors; every generated asset is reduced to exactly these colors with
hard edges (`scripts/art_gen/palette.py` is the single source of truth, `process.py` snaps to it).

**Core, read off the sprites and the icon:**

| Group | Hex |
|---|---|
| ink (outlines, shadows) | `#0c080a #140e14 #1c191c #240924 #28242b #350d2a #301b33` |
| rim (the characters' outline) | `#fff4d6` |
| bone | `#d9d7dc #dbcdcb #beaead #9a8b8a` |
| plum | `#6c4d6e #791267` |
| crimson | `#5e111f #9f1b29 #ff0000` |
| brown | `#4d2110 #642e11 #7f4a22 #a76232 #cf8944` |
| skin | `#f4a668 #f6d29c` |
| gold | `#b07f40 #e49b49 #f3be51` |
| moss | `#4c521a` |

**Scenery, lighter and duller ramps in the same hue families (dark to light):**

| Ramp | Hex |
|---|---|
| dusk (lilac) | `#5b4a78 #6e5d8c #8272a0 #9686b2 #aa9cc2 #bdb2d0 #cfc7dc #e0dae8` |
| slate | `#4f5870 #65708a #7b87a1 #929db6 #aab4c9` |
| rose | `#8a5a70 #a8708a #c48a9c #d9a5ac #ecc3b8 #f4dcc4` |
| stone | `#6a6470 #837d8a #9d97a4 #b7b1bd #d0cbd4` |
| sand | `#a08c78 #b9a58c #d2c1a4 #e6d8bf` |
| grass | `#6a7a3a #8a9a52 #a8b46c` |
| torch | `#d9692a #f6e08a` |
| banner | `#b83a45 #d86a70` |

Dark violet-black (`#1c0b18`-ish) is for outlines and shadows only, never for large areas of
scenery. Saturated colors (crimson, torch, gold) are accents.

## Pixel scale

- **Characters: 1x.** 64x64 frames, drawn 1 art pixel = 1 screen pixel (already done).
- **Scenery and UI: 2x.** They are made at 400x300 (half of the 800x600 game) and enlarged with
  nearest neighbor, so one art pixel is 2x2 screen pixels. Reasons: AI generation does not hold a
  true 1 px grid at 800x600, and chunkier scenery behind finer characters helps the characters
  read. This is a deliberate, single rule; there are no mixed scales inside one asset.
  (If the owner wants everything at 1x, the pipeline has one constant, `SCALE` in
  `scripts/art_gen/process.py`, but the detail gets noisy.)
- Text: pixel fonts only at whole multiples of their native grid (see Font).

## Outline rule

- Characters: 1 px light outline, `#fff4d6`, around the whole silhouette (PR #16, after the
  play-test: a dark character disappeared against a dark tree line).
- Scenery, platforms and UI: 1 px **dark** ink outline on the shapes that must be read as objects
  (platforms, buttons, panels, cursors, digits). Background scenery has no outline at all, only
  tone steps. So light outline means "a thing that moves", dark outline means "a thing you stand
  on or click".

## Light direction

Upper left, from the moon. Highlights sit on top and left edges (platform tops, button bevels,
panel borders), shadow and crimson trim on the bottom and right. Pressed buttons lose the shadow
and move down one pixel.

## Readability rule (owner, 2026-11-20)

Characters must stand out from every background.

1. Backgrounds are **lighter and duller** than the characters: mid-to-light dusk tones, saturation
   cut to 80%, luma graded into the 70 to 205 band. Characters' bodies are dark (vampire mean luma
   about 46, peasant about 80 against backgrounds at about 160) with the light outline.
2. **No dark band at standing height.** The strip between 40% and 90% of the height (where the
   characters run) has no dark shapes, no tree line, no black wall. Measured by
   `scripts/art_gen/mockups.py`: the minimum luma in that strip is 124 or more, the mean 154 to 166,
   for all 8 candidates.
3. Detail sits in the upper part and at the far left and right edges; the middle stays calm.
4. Platforms and ground are the darkest and most outlined scenery, so the standing surface always
   reads.

Known weak spot: the Arena platforms (sandstone) sit on a sandstone background; their dark outline
carries the contrast. Candidate B (cathedral) is more distinct from them.

## Backgrounds

800x600, one per level plus the menu, two moods each so the owner can pick:

| Screen | A (default) | B |
|---|---|---|
| Menu | gothic castle on a cliff under a big moon | graveyard gate, castle far away |
| Classic | moonlit mountain valley with a village | warm rose dusk, windmill and rooftops |
| Towers | castle courtyard, banners, battlements | spires and flying buttresses in fog |
| Arena | ruined stone arena with arches | cathedral ruin with a crimson rose window |

They are single images, not parallax layers: the style does not need scrolling (the map never
scrolls), and `ParallaxBackground`'s per-round re-randomizing would break the composed scenes.
The scene continues to the bottom edge; the ground strip is overlaid at `settings.GROUND_Y`.

## Platforms and ground

Per level, one material that matches its background: Classic mossy earth, Towers castle brick,
Arena sandstone. Each is a **3-slice sheet** (left cap 16 px, tiled middle 32 px that is a patch
plus its mirror so it repeats seamlessly, right cap 16 px) at the height that level's platforms use
in `settings.LEVELS`: Classic 50, Towers 30, Arena 20 px, plus a 50 px ground strip
(`platform_<level>.png`, `ground_<level>.png` in `assets/images/style/`). Any width in the level
tables works: caps plus as many middles as fit.

## UI

- **Buttons:** normal, hover, pressed, 224x64 px, no text (the label is drawn in code with the
  font). Candidate A is a forged iron plate, B a carved stone slab with gothic ends.
- **Panel/popup frame** and **level-select card frame:** 9-slice, 20 px border, flat interior.
  Candidate A iron with crimson gems, B stone with arch ornaments.
- **Cursor:** arrow, pointing hand, grabbing hand, about 28 px.
- **Countdown:** the glyphs 3, 2, 1, GO!, bone-white with a crimson lower edge and fang drips.
- **HUD** (drawn in code, palette colors only): ink boxes with a 2 px plum or crimson edge, a bar
  with a 1 px `#fff4d6` outline, labels in Silkscreen.

## Font

| | Candidate A (default) | Candidate B | Today |
|---|---|---|---|
| Titles | Jacquard 12 (gothic pixel blackletter) | Press Start 2P | Comic Neue |
| Buttons, HUD, labels | Silkscreen | Press Start 2P | Comic Neue |

All three are SIL OFL 1.1 static TTFs from Google Fonts (`google/fonts`, `ofl/`), license texts in
`licenses/assets/` and entries in `assets/SOURCES.yaml`. Jacquard 12 is only legible in mixed
case and at 24 px or larger, so it is for titles only ("The Hunted", "Select Level", "Credits");
everything the player has to read quickly is Silkscreen (caps, 8 px grid, used at 16 and 24).
Press Start 2P is the safe, more uniform alternative.

## How the assets are made

`scripts/art_gen/`: `prompts.py` (every prompt), `generate.py` (Codex image generation with the
sheets and icon as style references), `process.py` (crop, grade, palette snap, hard alpha, 3-slice,
2x), `mockups.py` (the devlog mockups), `shoot_today.py` (screenshots of current main). Generation
is not deterministic; the kept raw pictures are in `scripts/art_gen/raw/`.
