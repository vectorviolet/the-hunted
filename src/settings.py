from typing import TypedDict

VIRTUAL_W = 800
VIRTUAL_H = 600
FPS = 60
TITLE = "The Hunted"

# Pixel fonts bundled in assets/fonts/ (SIL OFL, licenses alongside) so text looks the same on
# every OS. Both are drawn without anti-aliasing and only at whole multiples of their native
# pixel grid, or the pixels blur: Jacquard 12 (12 px grid, a gothic blackletter) for titles only
# and in mixed case, Silkscreen (8 px grid, capitals) for everything else: sizes 16, 24, 48.
TITLE_FONT = "assets/fonts/Jacquard12-Regular.ttf"
UI_FONT = "assets/fonts/Silkscreen-Regular.ttf"
WINDOW_ICON = "assets/images/icon/icon_64.png"
FLOOR_Y = 490.0
GROUND_Y = (
    550  # visual ground-tile top; matches the player foot line when standing on FLOOR_Y
)


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


# Levels  — platform y must end in 0 so velocity steps land cleanly
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
            ((0, 400), 300, 50),
            ((500, 400), 300, 50),
            ((250, 250), 300, 50),
        ],
    },
    {
        "name": "Towers",
        "background": "towers",
        "style": "towers",
        "platforms": [
            ((0, 430), 220, 30),
            ((580, 430), 220, 30),
            ((150, 300), 220, 30),
            ((430, 300), 220, 30),
            ((310, 170), 180, 30),
        ],
    },
    {
        "name": "Arena",
        "background": "arena",
        "style": "arena",
        "platforms": [
            ((50, 480), 160, 20),
            ((590, 480), 160, 20),
            ((200, 370), 180, 20),
            ((420, 370), 180, 20),
            ((0, 260), 200, 20),
            ((600, 260), 200, 20),
            ((300, 190), 200, 20),
        ],
    },
]

# The menu's backdrop and ground art (assets/images/{background,ground}/).
MENU_BACKGROUND = "menu"
MENU_STYLE = "towers"

# Keep for backwards-compat during transition
PLATFORM_DEFS = LEVELS[0]["platforms"]
