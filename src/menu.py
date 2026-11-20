import pygame

from background import load_background
from buttons import (
    BTN_HOVER,
    BTN_NORMAL,
    BTN_PRESSED,
    BUTTON_FONT,
    centered_button_rect,
    make_button,
)
from countdown import CountdownGraphic, countdown_step
from credits import CreditSection, load_credit_sections
from cursor import CLICK, CLICK2, NORMAL
from entities import Platform
from pixelart import nine_slice
import settings
from settings import BONE, GROUND_Y

# The pages of the menu (Menu.page).
PAGE_MAIN, PAGE_MODE, PAGE_CREDITS, PAGE_THANKS = "main", "mode", "credits", "thanks"

IDLE = (
    100  # Game's countdown value while no countdown runs: the page and its buttons show
)

# Each page's buttons: name -> (label, rect). The two stacked pages share three slots.
_SLOT_TOPS = (150, 214, 278)
_RATE_SIZE = (440, 44)  # the popup's wide "leave a comment or rating" button
_RATE_FONT = 16
BUTTONS: dict[str, dict[str, tuple[str, pygame.Rect]]] = {
    PAGE_MAIN: {
        "play": ("PLAY", centered_button_rect(_SLOT_TOPS[0])),
        "credits": ("CREDITS", centered_button_rect(_SLOT_TOPS[1])),
        "exit": ("EXIT", centered_button_rect(_SLOT_TOPS[2])),
    },
    PAGE_MODE: {
        "vs_ai": ("VS AI", centered_button_rect(_SLOT_TOPS[0])),
        "pvp": ("PVP", centered_button_rect(_SLOT_TOPS[1])),
        "back": ("BACK", centered_button_rect(_SLOT_TOPS[2])),
    },
    PAGE_CREDITS: {"back": ("BACK", centered_button_rect(352))},
    PAGE_THANKS: {
        "rate": ("LEAVE A COMMENT OR RATING", centered_button_rect(250, _RATE_SIZE)),
        "back": ("BACK", centered_button_rect(318)),
    },
}
TITLES = {
    PAGE_MAIN: "The Hunted",
    PAGE_MODE: "The Hunted",
    PAGE_CREDITS: "Credits",
    PAGE_THANKS: "Thanks for playing!",
}
TITLE_CENTERS = {PAGE_MAIN: 80, PAGE_MODE: 80, PAGE_CREDITS: 72, PAGE_THANKS: 152}
THANKS_LINE = "Enjoyed The Hunted? Tell us what you think."

# The panels (images/ui/panel.png) behind the credits and the popup; both end above the
# players' heads.
PANEL_BORDER = 50  # px of the panel art's corners that keep their pixels
CREDITS_PANEL = pygame.Rect(130, 24, 700, 396)
THANKS_PANEL = pygame.Rect(160, 90, 640, 330)
PANELS = {PAGE_CREDITS: CREDITS_PANEL, PAGE_THANKS: THANKS_PANEL}
CREDITS_VIEW = pygame.Rect(170, 108, 620, 236)  # where the credits scroll
SCROLL_STEP = 24  # px per mouse-wheel notch or arrow-key press
CREDITS_LINE = 24  # px between the credits' text rows
CREDITS_GAP = 16  # extra px before each section's heading
SCROLLBAR_W = 6

TITLE_FONT_SIZE, TEXT_FONT_SIZE = (
    72,
    16,
)  # whole multiples of Jacquard 12's / Silkscreen's grid


def wrap_words(text: str, font: pygame.font.Font, width: int) -> list[str]:
    """`text` split at spaces into lines no wider than `width` (a lone long word stays whole)."""
    lines: list[str] = []
    current = ""
    for word in text.split():
        candidate = f"{current} {word}" if current else word
        if current and font.size(candidate)[0] > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    return [*lines, current] if current else lines


class Menu:
    """The main menu and its pages: PLAY / CREDITS / EXIT, the mode menu, the credits and the
    web build's "Thanks for playing" popup. `Game` decides what a click does; the menu knows the
    layout, the hover state and the scrolling, and draws the current `page`."""

    def __init__(self, window_w: int, window_h: int, cursor) -> None:
        self.cursor = cursor
        self.window_w = window_w
        self.window_h = window_h
        self.page = PAGE_MAIN
        self.scroll = 0  # how far the credits are scrolled, in px

        self._hover: str | None = None  # the hovered button of the current page
        self._pressed: str | None = None  # the button being pressed

        self._font_sm = pygame.font.Font(settings.UI_FONT, TEXT_FONT_SIZE)
        self._font_title = pygame.font.Font(settings.TITLE_FONT, TITLE_FONT_SIZE)
        self._lbl_p1 = self._font_sm.render("P1", False, BONE)
        self._lbl_p2 = self._font_sm.render("P2", False, BONE)

        self._background = load_background(
            settings.MENU_BACKGROUND, (window_w, window_h)
        )
        self._ground = Platform(
            (0, GROUND_Y),
            window_w,
            int(window_h - GROUND_Y),
            style=settings.MENU_STYLE,
            kind="ground",
        )
        panel = pygame.image.load("assets/images/ui/panel.png").convert_alpha()
        self._panels = {
            page: nine_slice(panel, PANEL_BORDER, rect.size)
            for page, rect in PANELS.items()
        }

        self._buttons: dict[tuple[str, str], dict[int, pygame.Surface]] = {
            (page, name): self._make_buttons(rect.size, label)
            for page, buttons in BUTTONS.items()
            for name, (label, rect) in buttons.items()
        }
        self._countdown_graphic = CountdownGraphic()
        self._credits = self._render_credits(load_credit_sections())

    @staticmethod
    def _make_buttons(size: tuple[int, int], label: str) -> dict[int, pygame.Surface]:
        font_size = _RATE_FONT if size == _RATE_SIZE else BUTTON_FONT
        return {
            state: make_button(state, size, label, font_size)
            for state in (BTN_NORMAL, BTN_PRESSED, BTN_HOVER)
        }

    def _shadowed(self, text: str, color: tuple[int, int, int]) -> pygame.Surface:
        """`text` in the UI font with a hard INK drop shadow."""
        face = self._font_sm.render(text, False, color)
        surface = pygame.Surface(
            (face.get_width() + 2, face.get_height() + 2), pygame.SRCALPHA
        )
        surface.blit(self._font_sm.render(text, False, settings.INK), (2, 2))
        surface.blit(face, (0, 0))
        return surface

    def _render_credits(self, sections: list[CreditSection]) -> pygame.Surface:
        """The whole credits text on one tall surface that `draw` scrolls through."""
        width = CREDITS_VIEW.width - 2 * SCROLLBAR_W
        rows: list[tuple[str, tuple[int, int, int], int]] = []  # text, color, extra gap
        for heading, lines in sections:
            rows.append((heading, settings.GOLD, CREDITS_GAP if rows else 0))
            for line in lines:
                rows += [
                    (part, BONE, 0) for part in wrap_words(line, self._font_sm, width)
                ]
        height = sum(CREDITS_LINE + gap for _, _, gap in rows)
        surface = pygame.Surface((CREDITS_VIEW.width, height), pygame.SRCALPHA)
        y = 0
        for text, color, gap in rows:
            y += gap
            row = self._shadowed(text, color)
            surface.blit(row, row.get_rect(midtop=(CREDITS_VIEW.width // 2, y)))
            y += CREDITS_LINE
        return surface

    # ------------------------------------------------------------------ pages

    def go_to(self, page: str) -> None:
        """Shows `page`: the credits start at the top and nothing is hovered."""
        self.page = page
        self.scroll = 0
        self._hover = self._pressed = None

    def button_rects(self) -> dict[str, pygame.Rect]:
        """The current page's buttons by name."""
        return {name: rect for name, (_, rect) in BUTTONS[self.page].items()}

    def button_at(self, pos) -> str | None:
        """The name of the current page's button under `pos`, if any."""
        for name, rect in self.button_rects().items():
            if rect.collidepoint(pos):
                return name
        return None

    def update_pointer(self, pos, pressed: bool) -> None:
        """Remembers which button the mouse is over and whether it is pressed."""
        name = self.button_at(pos)
        self._hover = name if name and not pressed else None
        self._pressed = name if name and pressed else None

    @property
    def max_scroll(self) -> int:
        """How far the credits can scroll: 0 when they fit."""
        return max(0, self._credits.get_height() - CREDITS_VIEW.height)

    def scroll_by(self, dy: int) -> None:
        """Scrolls the credits by `dy` px (positive is down), staying inside the text."""
        self.scroll = max(0, min(self.max_scroll, self.scroll + dy))

    # ------------------------------------------------------------------ drawing

    def draw(self, surface: pygame.Surface, countdown: int, p1, p2=None) -> None:
        """Draw the current page. Pass p2=None for single-player mode. While a countdown runs
        (countdown != IDLE) only the backdrop, the players and the countdown show."""
        surface.blit(self._background, (0, 0))
        self._ground.draw(surface)
        showing = countdown == IDLE
        has_panel = self.page in self._panels

        # A panel is drawn over the players' tags, so those pages show the players alone.
        self._draw_players(surface, p1, p2, labels=not has_panel)
        if showing:
            if has_panel:
                self._draw_panel(surface)
            self._draw_title(surface)
            self._draw_buttons(surface)

        # The buttons only exist before the countdown starts; afterwards it is a plain arrow.
        if showing:
            self.cursor.set_state(
                CLICK if self._hover else CLICK2 if self._pressed else NORMAL
            )
        else:
            self.cursor.set_state(NORMAL)

        step = countdown_step(countdown)
        if step is not None:
            self._countdown_graphic.draw(surface, step)

    def _draw_players(self, surface, p1, p2, labels: bool) -> None:
        players = [(p1, self._lbl_p1)]
        if p2 is not None:
            players.append((p2, self._lbl_p2))
        for p, lbl in players:
            if labels:
                surface.blit(
                    lbl, (int(p.x) + p.width // 4 + 8, int(p.y) - p.height // 2)
                )
            p.draw(surface)

    def _draw_title(self, surface: pygame.Surface) -> None:
        text = TITLES[self.page]
        face = self._font_title.render(text, False, settings.RIM)
        shadow = self._font_title.render(text, False, settings.CRIMSON)
        rect = face.get_rect(center=(self.window_w // 2, TITLE_CENTERS[self.page]))
        surface.blit(shadow, rect.move(3, 3))
        surface.blit(face, rect)

    def _draw_panel(self, surface: pygame.Surface) -> None:
        surface.blit(self._panels[self.page], PANELS[self.page])
        if self.page == PAGE_THANKS:
            line = self._shadowed(THANKS_LINE, BONE)
            surface.blit(line, line.get_rect(center=(self.window_w // 2, 220)))
        else:
            self._draw_credits(surface)

    def _draw_credits(self, surface: pygame.Surface) -> None:
        surface.blit(
            self._credits,
            CREDITS_VIEW.topleft,
            (0, self.scroll, CREDITS_VIEW.width, CREDITS_VIEW.height),
        )
        if not self.max_scroll:
            return
        track = pygame.Rect(
            CREDITS_VIEW.right - SCROLLBAR_W,
            CREDITS_VIEW.y,
            SCROLLBAR_W,
            CREDITS_VIEW.height,
        )
        thumb_h = max(16, track.h * CREDITS_VIEW.height // self._credits.get_height())
        thumb_y = track.y + (track.h - thumb_h) * self.scroll // self.max_scroll
        pygame.draw.rect(surface, settings.INK, track)
        pygame.draw.rect(surface, settings.PLUM, (track.x, thumb_y, track.w, thumb_h))

    def _draw_buttons(self, surface: pygame.Surface) -> None:
        for name, rect in self.button_rects().items():
            state = (
                BTN_HOVER
                if name == self._hover
                else BTN_PRESSED
                if name == self._pressed
                else BTN_NORMAL
            )
            surface.blit(self._buttons[(self.page, name)][state], rect)
