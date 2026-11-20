import pygame

from background import load_background
from buttons import BTN_HOVER, BTN_NORMAL, BTN_PRESSED, make_button
from countdown import CountdownGraphic, countdown_step
from cursor import CLICK, CLICK2, NORMAL
from entities import Platform
import settings
from settings import BONE, GROUND_Y

START_SIZE = (310, 100)
BUTTON_SIZE = (212, 44)
START_FONT, BUTTON_FONT = 48, 24  # Silkscreen sizes: whole multiples of its 8 px grid


class Menu:
    def __init__(self, window_w: int, window_h: int, cursor) -> None:
        self.cursor = cursor
        self.window_w = window_w
        self.window_h = window_h

        self._btn_1p_hover = self._btn_1p_click = False
        self._btn_2p_hover = self._btn_2p_click = False
        self._btn_start_hover = self._btn_start_click = False

        self._font_sm = pygame.font.Font(settings.UI_FONT, 16)
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

        self._start_btn = self._make_buttons(START_SIZE, "START", START_FONT)
        self._btn_1p = self._make_buttons(BUTTON_SIZE, "1 PLAYER", BUTTON_FONT)
        self._btn_2p = self._make_buttons(BUTTON_SIZE, "2 PLAYER", BUTTON_FONT)
        self._countdown_graphic = CountdownGraphic()

    @staticmethod
    def _make_buttons(
        size: tuple[int, int], label: str, font_size: int
    ) -> dict[int, pygame.Surface]:
        return {
            state: make_button(state, size, label, font_size)
            for state in (BTN_NORMAL, BTN_PRESSED, BTN_HOVER)
        }

    @staticmethod
    def _state(hover: bool, click: bool) -> int:
        return BTN_HOVER if hover else BTN_PRESSED if click else BTN_NORMAL

    def update_button_state(self, btn_name: str, hovered: bool, pressed: bool) -> None:
        setattr(self, f"_btn_{btn_name}_hover", hovered and not pressed)
        setattr(self, f"_btn_{btn_name}_click", hovered and pressed)

    def draw(self, surface: pygame.Surface, countdown: int, p1, p2=None) -> None:
        """Draw the main menu. Pass p2=None for single-player mode."""
        surface.blit(self._background, (0, 0))
        self._ground.draw(surface)
        cx, cy = self.window_w // 2, self.window_h // 2

        if countdown == 100:
            start = self._start_btn[
                self._state(self._btn_start_hover, self._btn_start_click)
            ]
            surface.blit(start, (cx - 155, cy - 240))
            btn_1p = self._btn_1p[self._state(self._btn_1p_hover, self._btn_1p_click)]
            btn_2p = self._btn_2p[self._state(self._btn_2p_hover, self._btn_2p_click)]
            surface.blit(btn_1p, (cx - 106, cy - 120))
            surface.blit(btn_2p, (cx - 106, cy - 56))

        # The buttons only exist before the countdown starts; afterwards it is a plain arrow.
        any_hover = self._btn_1p_hover or self._btn_2p_hover or self._btn_start_hover
        any_click = self._btn_1p_click or self._btn_2p_click or self._btn_start_click
        if countdown != 100:
            self.cursor.set_state(NORMAL)
        else:
            self.cursor.set_state(
                CLICK if any_hover else CLICK2 if any_click else NORMAL
            )

        players = [(p1, self._lbl_p1)]
        if p2 is not None:
            players.append((p2, self._lbl_p2))

        for p, lbl in players:
            surface.blit(lbl, (int(p.x) + p.width // 4 + 8, int(p.y) - p.height // 2))
            p.draw(surface)

        step = countdown_step(countdown)
        if step is not None:
            self._countdown_graphic.draw(surface, step)
