# Store page (itch.io)

The itch.io page at <https://umutcanekinci.itch.io/the-hunted> is edited by hand on itch.io. This
folder holds what goes into it:

- `description.html`: the page's description. Paste it into the description field in HTML mode. It
  uses only headings, paragraphs, lists, links, `strong`, `code` and one image, with no inline
  styles or tables, so it reads well on phones.
- `cover.png`: the cover (630x500, itch.io's cover size). It is the default pick from
  `candidates/` (the owner chooses, see [Cover](#checklist-for-the-edit-page)).
- `candidates/`: the three cover candidates, 630x500 each.

The release workflow (`.github/workflows/release.yml`) uploads the builds with Butler to the
`windows`, `linux`, `osx` and `html5` channels; it never touches the page text. The same builds
are on the [GitHub releases](https://github.com/vectorviolet/hunted/releases/latest).

The [Field values](#field-values) table at the end lists what each edit-page field holds or should
hold; the checklist items explain the reasoning. The tagline, the description wording, the tags
and the cover are proposals until the owner picks them.

## Checklist for the edit page

Fields that live outside the description, following itch.io's
[quality guidelines](https://itch.io/docs/creators/quality-guidelines):

- **Short description or tagline:** "A goofy vampire-versus-peasant chase for one or two
  players." (proposal; two alternatives are in [Field values](#field-values)). It does not repeat
  the title.
- **Classification:** Games. **Kind of project:** HTML (itch.io's name for a game that runs in
  the browser; the page also offers downloads, the Windows installer and the zips, as a second
  upload type). **Release status:** Released once a tagged release is on the page; In
  development before that (the owner's call).
- **Platforms:** Windows, macOS, Linux and Web (the four the release workflow builds).
- **Genre:** Platformer. (Action is the alternative.)
- **Tags:** see [Field values](#field-values) below.
- **Languages:** English (the game has one language).
- **Inputs:** Keyboard, Mouse. Two players share one keyboard in PVP; the mouse drives the menus.
- **Browser version:** the `html5` channel upload. After the first upload tick **This file will
  be played in the browser** on that file, set the embed size to **960 x 540** (the game's own
  canvas, 16:9) and tick **Fullscreen button**; leave mobile friendly off (it needs a keyboard).
  Tick **Click to launch in fullscreen** only if the owner prefers it. The game starts after one
  click on the frame (the browser needs it to unlock audio), so the description says so; F11
  toggles fullscreen in the page too. See "Browser build" in `CONTRIBUTING.md`.
- **AI disclosure:** answer it on the edit page to match the description's line:
  - **Graphics: yes.** The art (characters, backgrounds, platforms, buttons, cursor, countdown)
    was AI-generated with OpenAI Codex image generation and then cleaned up by script to one
    shared palette (`docs/design/art-style.md`).
  - **Code: yes.** Claude Code was a coding assistant; design, direction, playtesting and review
    are the developer's.
  - **Sound and music: no.** Both are CC0 packs (Kenney's interface sounds and Hydrogene's
    tracks, see `CREDITS.md`).
  - **Text:** yes if you count the store text and README, which were drafted with Claude and
    reviewed by the owner (Chokepoint's page ticks it the same way).
- **Screenshots:** uploaded to the page's gallery in this order (all in `docs/screenshots/`,
  1920x1080): `06_round_towers.png`, `07_round_arena.png`, `05_round_classic.png`,
  `02_mode_menu.png`, `04_level_select.png` and `01_main_menu.png`. Optional: `03_credits.png`.
  itch.io shows them apart from the description, so the description only embeds the preview GIF.
  `scripts/art_gen/shoot.py` and `scripts/art_gen/make_media.py` retake them (see
  [Retaking the media](#retaking-the-media)).
- **Images:** `description.html` links the GIF from GitHub so it works when pasted as is. Better:
  upload `docs/preview.gif` through itch.io's editor and swap the image on the page for the
  uploaded one, so it loads fast and doesn't break if the file moves in the repo.
- **Theme:** colors from the art palette, see [Theme settings](#theme-settings) below.
- **Cover:** `docs/store/cover.png` (630x500). Three candidates are in `docs/store/candidates/`;
  the default is `a-menu-scene.png` (the title card: both characters on the menu backdrop). The
  owner picks; then copy the pick over `cover.png` and upload it on the edit page.
- **GitHub social preview:** `docs/design/social-preview.png` (1280x640, GitHub's 2:1), made by
  `make_media.py social` from the menu scene. Upload it by hand in the repository's Settings >
  Social preview (GitHub has no API for it).
- **Banner and trailer:** none yet. A banner is optional on itch.io.

## Field values

What to set on the edit page, field by field (the owner edits the page by hand; copy from here).

| Field | Value |
|---|---|
| Title / project URL | The Hunted / `the-hunted` |
| Short description or tagline | A goofy vampire-versus-peasant chase for one or two players. Alternatives: "Chase or be chased: a pixel-art couch platformer where the roles swap every round." / "One vampire, one peasant, one screen. Catch them or shoot back." |
| Classification / kind / release status | Games / HTML (plus downloads) / the owner's call, see above |
| Pricing | the owner's choice (Chokepoint and Highrise use $0 or donate) |
| Uploads | `windows` (`hunted-windows.zip`, and the installer `hunted-windows-setup.exe` from the GitHub release if you want it on the page), `linux`, `osx` and `html5` come from the release workflow's butler jobs. Tick the matching platform on each file |
| Browser version | `html5` channel: play in the browser, 960 x 540, Fullscreen button on, mobile friendly off |
| Description | paste `docs/store/description.html` in HTML mode |
| Genre | Platformer |
| Tags (max 10; not the genre or platforms; proposal) | 2D, Pixel Art, Local Multiplayer, Singleplayer, Couch Co-op, Funny, Vampire, Arcade, AI Generated, Open Source |
| Languages | English |
| Inputs | Keyboard, Mouse |
| AI generation disclosure | **Yes.** Graphics (OpenAI Codex image generation, cleaned up) and Code (Claude Code as a coding assistant); not Sounds |
| Statement of AI usage (shown publicly) | The art is AI-generated with OpenAI Codex image generation and cleaned up to one palette; Claude Code was a coding assistant. Game design, art direction, playtesting and review by the developer. The music and sounds are CC0 packs. |
| App store links | none |
| Custom noun | leave blank |
| Download and install instructions | see the block below |
| Community | Comments suggested on, discussion board off (the owner decides) |
| Visibility and access | Public once the page is ready (the owner's step) |
| Cover image | `docs/store/cover.png` (630x500) |
| Gameplay video or trailer | none |
| Screenshots (3 to 5) | in the order listed in the Screenshots item above |

**Download and install instructions** (paste into the field):

```
Play it right here in the browser, or download a build.

Windows: run hunted-windows-setup.exe, or unzip hunted-windows.zip and run hunted.exe. The game isn't code-signed, so the first launch may show "Windows protected your PC": click More info, then Run anyway.
macOS: open Hunted.app. The app isn't signed, so macOS blocks the first launch: right-click it and choose Open.
Linux: run ./hunted/hunted from the unzipped folder.
```

## Theme settings

Proposed values for the theme editor ("Edit theme"), from the art palette (`src/settings.py`,
`docs/design/art-style.md`). Contrast was checked by eye against the dark backgrounds; recheck on
the live page.

| Group | Setting | Value |
|---|---|---|
| Color | BG | `#140e14` (ink) |
| Color | BG 2 | `#2c2150` (the palette's dark violet) |
| Color | Text | `#d9d7dc` (bone) |
| Color | Link | `#f3be51` (gold) |
| Color | Button / accent | `#9f1b29` (crimson) |
| Text | Font | a pixel font if the editor offers one, else the default |
| Layout | Screenshots | Auto (sidebar) |
| Images | Banner | none |

## Retaking the media

All of it runs headless from the repo root (the `art` group has Pillow):

```bash
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run --group art python scripts/art_gen/shoot.py
SDL_VIDEODRIVER=dummy SDL_AUDIODRIVER=dummy uv run --group art python scripts/art_gen/make_media.py
```

`shoot.py` writes the 960x540 frames to `scripts/art_gen/work/` (not committed);
`make_media.py` turns them into the README screenshots (1920x1080), `docs/preview.gif`, the cover
candidates, `cover.png` and the social preview. Pass step names to run only some of them
(`screenshots`, `gif`, `covers`, `social`). README and store media stay at full size; only
devlog images are capped at 1280 px wide.

When the game changes in a way players see (controls, levels, modes), update `description.html`
in the same PR and paste it again.
