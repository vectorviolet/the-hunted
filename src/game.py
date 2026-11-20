import random

import pygame
from pygamine import Application
from pygamine import Mouse
from pygamine import SplashScreen, standard_splash_media
import settings
from audio import AudioManager
from combat import CombatSystem
from countdown import END_FRAME
from cursor import CLICK, NORMAL, Cursor
from entities import Player, level_platforms
from input_handler import AIInputHandler, KeyboardInputHandler
from menu import (
    IDLE,
    PAGE_CREDITS,
    PAGE_MAIN,
    PAGE_MODE,
    PAGE_THANKS,
    SCROLL_STEP,
    Menu,
)
from renderer import GameRenderer
from util import web
from world import GameWorld


LEFT_BUTTON = 1  # the only mouse button that presses menu buttons and level cards


class Game(Application):
    STATE_MENU = "menu"
    STATE_LEVEL_SELECT = "level_select"
    STATE_GAME = "game"

    def __init__(self) -> None:
        pygame.mixer.pre_init(44100, -16, 2, 1024 * 3)
        self._cursor = Cursor()
        _mouse = Mouse()
        _mouse.cursor = self._cursor
        # Before the first set_mode(): X11 and macOS apply the icon only if it is set first.
        pygame.display.set_icon(pygame.image.load(settings.WINDOW_ICON))

        super().__init__(
            size=(settings.VIRTUAL_W, settings.VIRTUAL_H),
            title=settings.TITLE,
            fps=settings.FPS,
            mouse=_mouse,
            fixed_aspect=True,
        )
        _mouse.set_cursor_visible(False)

        # fixed_aspect=True locks self.window to (VIRTUAL_W, VIRTUAL_H) --
        # Hunted's entire layout (platforms, HUD, buttons) is hand-authored
        # in those fixed pixel coordinates, so everything draws directly
        # onto self.window; Application itself letterboxes/pillarboxes it
        # onto the real display and keeps self.mouse.position remapped
        # into this same space, so no separate canvas/present/mouse-remap
        # step is needed here anymore (see the previous, hand-rolled
        # _fit_rect/_present_canvas/_authored_mouse_pos this replaced).

        # The splash decodes its video frames on a thread; the browser build has
        # none and goes straight to the menu (Application skips a None splash).
        if not web.is_web():
            self.splash = SplashScreen(standard_splash_media(), skip_completely=True)

        self._world = GameWorld(
            window_w=settings.VIRTUAL_W, window_h=settings.VIRTUAL_H
        )
        self._world.platforms = level_platforms(0)

        self._menu = Menu(settings.VIRTUAL_W, settings.VIRTUAL_H, self._cursor)
        self._audio = AudioManager()
        self._renderer = GameRenderer(self.window, self._world)
        self._combat = CombatSystem(self._world)

        self._font_hud = pygame.font.Font(settings.UI_FONT, 16)
        self._score_surfs: list[pygame.Surface] = []

        self._current_level = 0
        self._state = self.STATE_MENU
        self._vampire: Player | None = None
        self._peasant: Player | None = None
        self._countdown = IDLE
        self._intro_seq = random.choice((1, 2, 3))
        self._intro_flag = False

        self._p1 = self._make_player(
            (self._world.platforms[1].x - 64 + 18, settings.FLOOR_Y), "R"
        )
        self._p2 = self._make_player(
            (
                self._world.platforms[0].x + self._world.platforms[0].width - 17,
                settings.FLOOR_Y,
            ),
            "L",
            is_p2=True,
        )
        self._p1.left = True
        self._p1.be_peasant()
        self._p2.be_peasant()
        self._bind_ai()
        self._refresh_scores()

    # ------------------------------------------------------------------ helpers

    def _make_player(self, location, control: str, is_p2: bool = False) -> Player:
        if not self._world.two_players:
            handler = AIInputHandler() if is_p2 else KeyboardInputHandler("RL")
        else:
            handler = KeyboardInputHandler(control)
        return Player(self._world, location, handler)

    def _bind_ai(self) -> None:
        if isinstance(self._p2._input, AIInputHandler):
            self._p2._input.bind(self._p2, self._p1)

    def _refresh_scores(self) -> None:
        self._score_surfs = [
            self._font_hud.render(f"P1  {self._p1.score}", False, settings.BONE),
            self._font_hud.render(f"P2  {self._p2.score}", False, settings.BONE),
        ]

    def _reset_players(self) -> None:
        self._p1 = self._make_player(
            (self._world.platforms[1].x - 64 + 18, settings.FLOOR_Y), "R"
        )
        self._p2 = self._make_player(
            (
                self._world.platforms[0].x + self._world.platforms[0].width - 17,
                settings.FLOOR_Y,
            ),
            "L",
            is_p2=True,
        )
        self._p1.left = True
        self._p1.be_peasant()
        self._p2.be_peasant()
        self._bind_ai()
        self._intro_seq = random.choice((1, 2, 3))
        self._intro_flag = False
        self._refresh_scores()

    # -------------------------------------------------------- Application overrides

    def show_splash(self) -> None:
        super().show_splash()
        # Only now: the splash plays the publisher clip's own audio first.
        self._audio.play_menu()

    def cycle_window_mode(self, step: int = 1) -> None:
        # F11. The browser has no window modes; it toggles the page's fullscreen. Kept here
        # for now; the engine-level version is vectorviolet/pygamine#58.
        if web.is_web():
            web.toggle_fullscreen()
        else:
            super().cycle_window_mode(step)

    def _handle_core_event(self, event: pygame.event.Event) -> None:
        # Closing the window always quits, from any page or state; only Esc goes back.
        if event.type == pygame.QUIT:
            super().on_exit_request()
        else:
            super()._handle_core_event(event)

    def on_exit_request(self) -> None:
        """Esc: go back one page, like a BACK button. On the main
        menu that is EXIT. In the game it returns to the main menu."""
        if self._state == self.STATE_GAME:
            self._audio.stop_game()
            self._world.bullets.clear()
            self._back_to_menu(PAGE_MAIN)
        elif self._state == self.STATE_LEVEL_SELECT:
            self._back_to_menu(PAGE_MODE)
        else:
            self._menu_back()

    def _back_to_menu(self, page: str) -> None:
        """Leaves the level select or the game for the menu's `page`, with its music."""
        self._reset_players()
        self._audio.play_menu()
        self._countdown = IDLE
        self._menu.go_to(page)
        self._state = self.STATE_MENU

    def handle_event(self, event: pygame.event.Event) -> None:
        if self._state == self.STATE_MENU:
            self._handle_menu_event(event)
        elif self._state == self.STATE_LEVEL_SELECT:
            self._handle_level_select_event(event)

    def update(self) -> None:
        if self._state == self.STATE_MENU:
            self._update_menu()
        elif self._state == self.STATE_LEVEL_SELECT:
            self._update_level_select()
        elif self._state == self.STATE_GAME:
            self._update_game()

    def draw(self) -> None:
        pos = self.mouse.position
        if self._state == self.STATE_MENU:
            p2 = self._p2 if self._world.two_players else None
            self._menu.draw(self.window, self._countdown, self._p1, p2)
        elif self._state == self.STATE_LEVEL_SELECT:
            self._renderer.draw_level_select(pos, pygame.mouse.get_pressed()[0])
        elif self._state == self.STATE_GAME:
            assert self._vampire is not None
            self._renderer.draw_game(
                self._p1,
                self._p2,
                self._vampire,
                self._current_level,
                self._score_surfs,
            )

    # -------------------------------------------------------------------- menu

    def _handle_menu_event(self, event: pygame.event.Event) -> None:
        if self._countdown != IDLE:
            return  # the page's buttons are gone while the countdown runs
        if event.type == pygame.MOUSEBUTTONUP and event.button == LEFT_BUTTON:
            name = self._menu.button_at(self.mouse.position)
            if name is not None:
                self._press_menu_button(name)
        elif self._menu.page == PAGE_CREDITS:
            if event.type == pygame.MOUSEWHEEL:
                self._menu.scroll_by(-event.y * SCROLL_STEP)
            elif event.type == pygame.KEYDOWN and event.key in (
                pygame.K_UP,
                pygame.K_DOWN,
            ):
                self._menu.scroll_by(
                    SCROLL_STEP if event.key == pygame.K_DOWN else -SCROLL_STEP
                )

    def _press_menu_button(self, name: str) -> None:
        page = self._menu.page
        if name == "back":
            self._menu_back()
        elif page == PAGE_MAIN:
            if name == "play":
                self._menu.go_to(PAGE_MODE)
            elif name == "credits":
                self._menu.go_to(PAGE_CREDITS)
            else:
                self._exit_game()
        elif page == PAGE_MODE:
            self._start_mode(two_players=name == "pvp")
        else:  # the popup's "leave a comment or rating" link
            web.open_in_new_tab(settings.ITCH_URL)

    def _start_mode(self, two_players: bool) -> None:
        """VS AI or PVP was picked: set the controls and start the countdown."""
        self._world.two_players = two_players
        self._p1.control = "R" if two_players else "RL"
        if two_players:
            self._p2.control = "L"
        self._countdown = 0

    def _menu_back(self) -> None:
        """BACK or Esc on a menu page: one page up (the main menu for every page above it).
        On the main menu, EXIT."""
        if self._menu.page == PAGE_MAIN:
            self._exit_game()
        else:
            self._countdown = IDLE  # Esc during the countdown cancels it
            self._menu.go_to(PAGE_MAIN)

    def _exit_game(self) -> None:
        """EXIT, or Esc on the main menu. The browser build can't close its tab, so it shows
        the "Thanks for playing" popup instead of quitting."""
        if web.is_web():
            self._menu.go_to(PAGE_THANKS)
        else:
            super().on_exit_request()

    def _update_menu(self) -> None:
        self._menu.update_pointer(self.mouse.position, pygame.mouse.get_pressed()[0])
        self._step_intro()

        if self._countdown < IDLE:
            self._countdown += 1
        if self._countdown == END_FRAME:
            self._audio.pause_all()
            self._audio.stop_menu()
            self._state = self.STATE_LEVEL_SELECT

    def _step_intro(self) -> None:
        if self._world.two_players:
            if self._intro_seq == 1:
                self._p1.intro_jump()
                if self._p1.y <= settings.FLOOR_Y - 150:
                    self._intro_flag = True
                if self._intro_flag:
                    self._p2.intro_jump()
            elif self._intro_seq == 2:
                self._p1.intro_jump()
                self._p2.intro_jump()
            else:
                self._p2.intro_jump()
                if self._p2.y <= settings.FLOOR_Y - 150:
                    self._intro_flag = True
                if self._intro_flag:
                    self._p1.intro_jump()
        else:
            self._p1.intro_jump()

    # ---------------------------------------------------------------- level select

    def _update_level_select(self) -> None:
        pos = self.mouse.position
        any_hover = self._renderer.back_rect().collidepoint(pos) or any(
            self._renderer.level_card_rect(i).collidepoint(pos)
            for i in range(len(settings.LEVELS))
        )
        self._cursor.set_state(CLICK if any_hover else NORMAL)

    def _handle_level_select_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONUP and event.button == LEFT_BUTTON:
            pos = self.mouse.position
            if self._renderer.back_rect().collidepoint(pos):
                self._back_to_menu(PAGE_MODE)
                return
            for i in range(len(settings.LEVELS)):
                if self._renderer.level_card_rect(i).collidepoint(pos):
                    self._current_level = i
                    self._world.platforms = level_platforms(i)
                    self._reset_players()
                    self._enter_game()
                    return

    # ---------------------------------------------------------------------- game

    def _enter_game(self) -> None:
        for p in (self._p1, self._p2):
            p.y = settings.FLOOR_Y
            p.vel_y = p.vel_x = 0.0
            p.on_ground = True
            p.hp = settings.MAX_HP

        self._audio.play_game()

        vampire = random.choice((self._p1, self._p2))
        vampire.be_vampire()
        self._vampire = vampire
        self._peasant = self._p2 if vampire is self._p1 else self._p1

        self._cursor.set_state(NORMAL)
        self._state = self.STATE_GAME

    def _update_game(self) -> None:
        self._p1.update()
        self._p2.update()
        assert self._vampire is not None and self._peasant is not None
        winner = self._combat.resolve(self._vampire, self._peasant)
        if winner is not None:
            winner.score += 1
            self._vampire, self._peasant = self._combat.begin_round(
                self._vampire, self._p1, self._p2
            )
            self._refresh_scores()
