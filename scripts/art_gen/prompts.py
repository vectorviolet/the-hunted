"""Prompts for the art-style candidates (issue #19, phase 1).

Every job is sent to OpenAI Codex image generation by ``generate.py`` with the three style
references attached (vampire sheet, peasant sheet, icon A). ``kind`` tells ``process.py`` how
to clean the result up. Outputs are not deterministic: re-running makes new pictures, so the
raw files that were picked are kept in ``scripts/art_gen/raw/``.
"""

STYLE = (
    "Crisp retro pixel art in exactly the style of the attached reference images (the vampire "
    "and peasant walk sheets and the vampire face icon): hard pixel edges, NO anti-aliasing, "
    "no blur, no gradients, no dithering noise, no painterly texture, a small limited palette "
    "(violet-black, deep purple, deep blue, teal, bone white, crimson, warm torch orange, "
    "straw gold, moss green, brown). Light comes from the upper left (the moon). "
    "No text, no letters, no people, no creatures, no watermark."
)

BG_RULES = (
    "This is a game background behind two small characters that run left and right across the "
    "middle and lower middle of the picture (one is a black-and-crimson vampire, the other a "
    "peasant in warm brown and gold). Night or deep-dusk mood, mid-dark values with real "
    "saturation: deep blue, teal and violet, cool and moody, with a pale moon and a few warm "
    "torch or window lights as accents. In the area between 40% and 90% of the height keep the "
    "values mid-dark (not black, not bright): NO near-black shapes, NO black silhouettes or dark "
    "tree line there, and no saturated red or crimson near the middle (red is reserved for the "
    "vampire). Strong detail in the upper part and at the far left and right edges; the middle "
    "stays calm but is a rich cool color with soft texture, not a flat fill. "
    "The scene continues to the bottom edge (no ground strip is needed, it is added later). "
    "Wide landscape image, 1536x1024, side view, flat 2D, no perspective floor."
)

MAGENTA = "on a perfectly flat solid magenta (#FF00FF) background, nothing else in the picture"

BACKGROUNDS = {
    "bg_menu_a": "A gothic vampire castle on a distant cliff under a huge pale moon, drifting "
    "clouds, a few small bats, quiet misty valley below. Main-menu mood: grand and calm.",
    "bg_menu_b": "A hilltop graveyard at night with an iron gate and leaning stone crosses far "
    "away, the castle tiny on the horizon, moon behind thin clouds, low fog. Main-menu mood: "
    "eerie and quiet.",
    "bg_classic_a": "Moonlit mountain valley at night: layered deep blue and teal mountains with pale snow caps, a few "
    "scattered pines far away, a tiny village with glowing windows at the horizon, a big "
    "pale moon.",
    "bg_classic_b": "A deep violet dusk over rolling teal hills: indigo sky with a band of dim magenta-orange glow "
    "at the horizon, a windmill and village rooftops with lit windows far away, a low pale moon.",
    "bg_towers_a": "A castle courtyard at night: blue-gray stone walls with battlements and "
    "red banners on the far left and right, torches, a tall gothic window glowing, the castle "
    "on a hill in the distance, pale moon. Open misty sky in the middle.",
    "bg_towers_b": "A skyline of tall gothic spires and tower tops seen far away through "
    "deep blue fog at night, tiny glowing windows, flying buttresses, pale moon, open sky in the "
    "middle.",
    "bg_arena_a": "A ruined ancient stone arena at twilight: crumbling arches and broken "
    "columns of cool blue-gray stone at the far left and right, hanging torches, sandy haze, a pale "
    "moon over the open middle.",
    "bg_arena_b": "The inside of a vast gothic cathedral ruin: tall blue-gray stone pillars and "
    "pointed arches at the far left and right, a large rose window glowing violet and amber high up, "
    "dust rays, open hazy nave in the middle.",
}

# name -> (kind, prompt)
# kind: "bg" | "slab" | "ui_buttons" | "ui_panel" | "ui_cursor" | "ui_digits"
JOBS: dict[str, tuple[str, str]] = {}
for _name, _scene in BACKGROUNDS.items():
    JOBS[_name] = ("bg", f"{STYLE} {_scene} {BG_RULES}")

_SLAB = (
    "A single long horizontal platform slab for a 2D side-scrolling platform game, seen from "
    "the side, filling the width of the picture, about five times as long as it is tall, with "
    "a thin lit top surface (light from the upper left), a thicker front face, and clean "
    "square-cut ends. Nothing else in the picture, no shadow, no background, "
    f"{MAGENTA}. 1536x1024."
)
JOBS["slab_classic"] = (
    "slab",
    f"{STYLE} Material: dusk-lit earth with a mossy green grass top and a brown dirt and small "
    f"stone face. {_SLAB}",
)
JOBS["slab_towers"] = (
    "slab",
    f"{STYLE} Material: light gray castle stone bricks with a pale lilac lit top edge. {_SLAB}",
)
JOBS["slab_arena"] = (
    "slab",
    f"{STYLE} Material: weathered pale sandstone blocks with cracks and a bone-white lit top "
    f"edge. {_SLAB}",
)

_BTN_COMMON = (
    "A UI kit sheet for a game menu: the same wide rectangular button drawn three times, "
    "stacked vertically with space between them, each about 3.5 times as wide as tall, with "
    "NO text on them. Top: normal. Middle: hover (lighter and brighter, slightly glowing). "
    "Bottom: pressed (darker, the face pushed down one pixel, shadow gone). 1 px dark outline "
    f"on every shape, light from the upper left, {MAGENTA}. 1536x1024."
)
JOBS["ui_buttons_a"] = (
    "ui_buttons",
    f"{STYLE} Button style: forged dark iron plate with purple-black face, bone-white bevel "
    f"highlight on the top and left edges, four small rivets, crimson inner trim. {_BTN_COMMON}",
)
JOBS["ui_buttons_b"] = (
    "ui_buttons",
    f"{STYLE} Button style: aged parchment-colored stone slab with a carved dark purple border, "
    f"pointed gothic arch notches at both ends, crimson gem in the corners. {_BTN_COMMON}",
)

_PANEL_COMMON = (
    "Two UI frames for a game, side by side with space between them, both with an EMPTY flat "
    "interior (one calm solid fill color, no pattern, no text): left, a large popup panel "
    "frame (about 4:3, large); right, a smaller tall level-select card frame (about 3:4). "
    "The frames have a decorative border about 24 pixels thick with corner ornaments and a "
    f"plain straight middle part of each edge (so it can be 9-sliced), {MAGENTA}. 1536x1024."
)
JOBS["ui_panel_a"] = (
    "ui_panel",
    f"{STYLE} Frame style: dark violet-black interior, forged iron border with rivets and "
    f"bone-white highlights, small crimson corner gems. {_PANEL_COMMON}",
)
JOBS["ui_panel_b"] = (
    "ui_panel",
    f"{STYLE} Frame style: deep purple interior, carved light gray stone border with small "
    f"gothic arch ornaments in the corners and thin crimson trim. {_PANEL_COMMON}",
)

JOBS["ui_cursor"] = (
    "ui_cursor",
    f"{STYLE} Three mouse cursors for a vampire game, drawn big and spaced in one row with "
    "lots of space between them: (1) a plain arrow pointer, (2) a pointing hand cursor with "
    "the index finger up, (3) a closed grabbing/pressed hand. Bone-white fill, 1 px "
    f"violet-black outline, tiny crimson accent. {MAGENTA}. 1536x1024.",
)
JOBS["ui_digits"] = (
    "ui_digits",
    f"{STYLE} The big countdown characters 3, 2, 1 and the word GO! drawn as one row of four "
    "large separate glyphs with lots of space between them, chunky blocky pixel lettering with "
    "a bone-white face, a 1 px violet-black outline, a crimson lower shadow edge and a gothic "
    f"touch (tiny fang points). {MAGENTA}. 1536x1024.",
)
