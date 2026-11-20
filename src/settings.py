from typing import TypedDict

# The game is drawn on a 960x540 (16:9) canvas. pygamine scales it with nearest-neighbor
# to the window: fullscreen on a 1920x1080 screen is an exact 2x, so the pixels stay sharp.
VIRTUAL_W = 960
VIRTUAL_H = 540
FPS = 60
TITLE = "The Hunted"

# Pixel fonts bundled in assets/fonts/ (SIL OFL, licenses alongside) so text looks the same on
# every OS. Both are drawn without anti-aliasing and only at whole multiples of their native
# pixel grid, or the pixels blur: Jacquard 12 (12 px grid, a gothic blackletter) for titles only
# and in mixed case, Silkscreen (8 px grid, capitals) for everything else: sizes 16, 24, 48.
TITLE_FONT = "assets/fonts/Jacquard12-Regular.ttf"
UI_FONT = "assets/fonts/Silkscreen-Regular.ttf"
WINDOW_ICON = "assets/images/icon/icon_64.png"
GROUND_HEIGHT = 50  # the ground strip, drawn at the bottom of the canvas
GROUND_Y = VIRTUAL_H - GROUND_HEIGHT  # visual ground-tile top (490)
FLOOR_Y = float(
    GROUND_Y - 60
)  # a player's y when standing on the ground: the foot line is
# at the ground tile's top


# Physics
GRAVITY = 0.5
JUMP_POWER = -14.0  # negative = upward
MAX_FALL_SPEED = 14.0
ACCEL = 1.5  # horizontal acceleration per frame
FRICTION = 0.75  # horizontal deceleration multiplier
PLAYER_SPEED = 5.0
VAMPIRE_SPEED = 6.5

# Combat
MAX_HP = 100
BULLET_DAMAGE = 10
CONTACT_DAMAGE = 1  # HP per frame while vampire overlaps peasant
SHOOT_COOLDOWN = 18  # frames between shots
BULLET_SPEED = 5
BULLET_RADIUS = 5
MAX_BULLETS = 5

# Colors
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
MAROON = (128, 0, 0)
GREEN = (0, 128, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
DARK_BG = (15, 15, 25)
PANEL_BG = (20, 20, 35)
HP_GREEN = (138, 154, 82)
HP_YELLOW = (243, 190, 81)
HP_RED = (216, 106, 112)
LIGHT_GREY = (180, 180, 180)
MID_GREY = (90, 90, 110)

# The art style's palette (docs/design/art-style.md) for everything drawn in code.
INK = (20, 14, 20)  # #140e14, the palette's violet-black: plates, outlines, shadows
RIM = (255, 244, 214)  # the characters' outline color; also bar outlines and titles
BONE = (217, 215, 220)  # text
PLUM = (108, 77, 110)  # plate edges
CRIMSON = (159, 27, 41)  # P2's plate edge, title shadows
SLATE = (79, 88, 112)  # P1's plate edge
GOLD = (243, 190, 81)  # hints, bullets
BULLET_COLOR = GOLD


# Levels  — platform y must end in 0 so velocity steps land cleanly. Laid out on the 960x540
# canvas: the old 800x600 layouts stretched 1.2x sideways so the platforms span the whole width.
# The tiers are spaced evenly between the ground (490) and the top platform, which sits at 150 or
# lower: a player standing on it has its role tag and health bar (110 px above the platform) clear
# of the HUD at the top (34 px). Every step is at most 150 px (Classic's, as always), under the
# jump's 189 px apex.
class Level(TypedDict):
    name: str
    background: str  # assets/images/background/<background>.png
    style: str  # platform and ground art: assets/images/{platform,ground}/<style>.png
    platforms: list[tuple[tuple[int, int], int, int]]


LEVELS: list[Level] = [
    {
        "name": "Classic",
        "background": "classic",
        "style": "classic",
        "platforms": [
            ((0, 340), 360, 50),
            ((600, 340), 360, 50),
            ((300, 190), 360, 50),
        ],
    },
    {
        "name": "Towers",
        "background": "towers",
        "style": "towers",
        "platforms": [
            ((0, 380), 264, 30),
            ((696, 380), 264, 30),
            ((180, 260), 264, 30),
            ((516, 260), 264, 30),
            ((372, 150), 216, 30),
        ],
    },
    {
        "name": "Arena",
        "background": "arena",
        "style": "arena",
        "platforms": [
            ((60, 410), 192, 20),
            ((708, 410), 192, 20),
            ((240, 330), 216, 20),
            ((504, 330), 216, 20),
            ((0, 240), 240, 20),
            ((720, 240), 240, 20),
            ((360, 150), 240, 20),
        ],
    },
]

# The menu's backdrop and ground art (assets/images/{background,ground}/).
MENU_BACKGROUND = "menu"
MENU_STYLE = "towers"

# Keep for backwards-compat during transition
PLATFORM_DEFS = LEVELS[0]["platforms"]
