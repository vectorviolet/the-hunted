"""Game() pulls in the full asset tree (sprites, sounds, the parallax
background) -- constructing it is exactly what scripts/smoke_test.py already
does headlessly for CI, so it's safe to build once here too. `game` is
module-scoped for the same reason; every test sets its own `_state` (and any
other precondition it needs) before acting, so sharing the instance across
tests in this file is safe -- exactly the pattern scripts/smoke_test.py
itself follows by cycling one Game() through every state in sequence."""

import pygame
import pytest

import settings
from cursor import CLICK, NORMAL
from countdown import END_FRAME
from game import Game
from input_handler import AIInputHandler
from menu import (
    IDLE,
    PAGE_CREDITS,
    PAGE_MAIN,
    PAGE_MODE,
    PAGE_THANKS,
    SCROLL_STEP,
)


@pytest.fixture(scope="module")
def game():
    return Game()


def click(game_, position):
    game_.mouse.position = position
    game_.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP))


def test_game_boots_and_cycles_through_every_state(game):
    # Mirrors scripts/smoke_test.py.
    assert game._state == Game.STATE_MENU
    game.update()
    game.draw()

    game._state = Game.STATE_LEVEL_SELECT
    game.update()
    game.draw()

    game._enter_game()
    assert game._state == Game.STATE_GAME
    game.update()
    game.draw()


def show(game_, page):
    """Puts the game on the menu's `page`, no countdown running."""
    game_._state = Game.STATE_MENU
    game_._countdown = IDLE
    game_._menu.go_to(page)


def click_button(game_, name):
    click(game_, game_._menu.button_rects()[name].center)


def press(game_, key):
    event = pygame.event.Event(pygame.KEYDOWN, key=key)
    game_._handle_core_event(event)  # what the Application does with every event,
    game_.handle_event(event)  # then hands it on


def test_the_main_menu_has_play_credits_and_exit(game):
    show(game, PAGE_MAIN)

    assert list(game._menu.button_rects()) == ["play", "credits", "exit"]


def test_play_opens_the_mode_menu(game):
    show(game, PAGE_MAIN)

    click_button(game, "play")

    assert game._menu.page == PAGE_MODE
    assert list(game._menu.button_rects()) == ["vs_ai", "pvp", "back"]
    assert game._countdown == IDLE


def test_credits_opens_the_credits_page(game):
    show(game, PAGE_MAIN)

    click_button(game, "credits")

    assert game._menu.page == PAGE_CREDITS


def test_exit_quits_on_desktop(game, monkeypatch):
    show(game, PAGE_MAIN)
    calls = []
    monkeypatch.setattr(game, "exit", lambda: calls.append(True))

    click_button(game, "exit")

    assert calls == [True]


def test_a_click_that_misses_every_button_does_nothing(game):
    show(game, PAGE_MAIN)

    click(game, (5, 5))

    assert game._menu.page == PAGE_MAIN


def test_vs_ai_selects_single_player_and_starts_the_countdown(game):
    show(game, PAGE_MODE)

    click_button(game, "vs_ai")

    assert game._world.two_players is False
    assert game._p1.control == "RL"
    assert game._countdown == 0


def test_pvp_selects_two_player_and_starts_the_countdown(game):
    show(game, PAGE_MODE)

    click_button(game, "pvp")

    assert game._world.two_players is True
    assert game._p1.control == "R"
    assert game._p2.control == "L"
    assert game._countdown == 0


def test_buttons_are_dead_while_the_countdown_runs(game):
    show(game, PAGE_MODE)
    game._countdown = 20

    click_button(game, "pvp")

    assert game._countdown == 20  # not restarted
    assert game._menu.page == PAGE_MODE


def test_mode_menu_back_returns_to_the_main_menu(game):
    show(game, PAGE_MODE)

    click_button(game, "back")

    assert game._menu.page == PAGE_MAIN


def test_credits_back_returns_to_the_main_menu(game):
    show(game, PAGE_CREDITS)

    click_button(game, "back")

    assert game._menu.page == PAGE_MAIN


def test_the_menu_chain_goes_down_and_back_up_page_by_page(game):
    show(game, PAGE_MAIN)
    click_button(game, "play")
    click_button(game, "vs_ai")
    game._countdown = END_FRAME - 1
    game._update_menu()
    assert game._state == Game.STATE_LEVEL_SELECT

    click(game, game._renderer.back_rect().center)  # level select BACK
    assert (game._state, game._menu.page) == (Game.STATE_MENU, PAGE_MODE)
    assert game._countdown == IDLE

    click_button(game, "back")  # mode menu BACK
    assert (game._state, game._menu.page) == (Game.STATE_MENU, PAGE_MAIN)


def test_level_select_back_restarts_the_menu_music_and_resets_the_players(
    game, monkeypatch
):
    game._state = Game.STATE_LEVEL_SELECT
    played = []
    monkeypatch.setattr(game._audio, "play_menu", lambda: played.append(True))
    old_p1 = game._p1

    click(game, game._renderer.back_rect().center)

    assert played == [True]
    assert game._p1 is not old_p1


@pytest.mark.parametrize("page", [PAGE_MODE, PAGE_CREDITS, PAGE_THANKS])
def test_esc_goes_back_to_the_main_menu_like_the_back_button(game, page):
    show(game, page)

    press(game, pygame.K_ESCAPE)

    assert game._state == Game.STATE_MENU
    assert game._menu.page == PAGE_MAIN


def test_esc_during_the_countdown_cancels_it(game):
    show(game, PAGE_MODE)
    game._countdown = 20

    press(game, pygame.K_ESCAPE)

    assert game._countdown == IDLE
    assert game._menu.page == PAGE_MAIN


def test_esc_on_the_level_select_goes_back_to_the_mode_menu(game):
    game._state = Game.STATE_LEVEL_SELECT

    press(game, pygame.K_ESCAPE)

    assert (game._state, game._menu.page) == (Game.STATE_MENU, PAGE_MODE)


def test_esc_on_the_main_menu_quits_on_desktop(game, monkeypatch):
    show(game, PAGE_MAIN)
    calls = []
    monkeypatch.setattr(game, "exit", lambda: calls.append(True))

    press(game, pygame.K_ESCAPE)

    assert calls == [True]


def test_esc_in_the_game_returns_to_the_main_menu(game):
    game._menu.go_to(PAGE_MODE)
    game._state = Game.STATE_GAME

    press(game, pygame.K_ESCAPE)

    assert (game._state, game._menu.page) == (Game.STATE_MENU, PAGE_MAIN)


@pytest.mark.parametrize("how", ["exit button", "esc"])
def test_in_the_browser_exit_opens_the_thanks_popup(game, monkeypatch, how):
    monkeypatch.setattr("util.web.is_web", lambda: True)
    monkeypatch.setattr(game, "exit", lambda: pytest.fail("a tab can't be closed"))
    show(game, PAGE_MAIN)

    if how == "esc":
        press(game, pygame.K_ESCAPE)
    else:
        click_button(game, "exit")

    assert game._menu.page == PAGE_THANKS
    assert list(game._menu.button_rects()) == ["rate", "back"]


def test_the_popups_back_button_and_esc_close_it(game, monkeypatch):
    monkeypatch.setattr("util.web.is_web", lambda: True)
    show(game, PAGE_THANKS)
    click_button(game, "back")
    assert game._menu.page == PAGE_MAIN

    show(game, PAGE_THANKS)
    press(game, pygame.K_ESCAPE)
    assert game._menu.page == PAGE_MAIN


def test_the_popups_rate_button_opens_the_itch_page_in_a_new_tab(game, monkeypatch):
    opened = []
    monkeypatch.setattr("util.web.is_web", lambda: True)
    monkeypatch.setattr("util.web.open_in_new_tab", opened.append)
    show(game, PAGE_THANKS)

    click_button(game, "rate")

    assert opened == ["https://umutcanekinci.itch.io/the-hunted"]
    assert game._menu.page == PAGE_THANKS


def test_the_credits_scroll_with_the_wheel_and_the_arrow_keys(game):
    show(game, PAGE_CREDITS)
    assert game._menu.max_scroll > 0  # the credits don't fit: they scroll

    game.handle_event(pygame.event.Event(pygame.MOUSEWHEEL, x=0, y=-1))
    assert game._menu.scroll == SCROLL_STEP
    game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_DOWN))
    assert game._menu.scroll == 2 * SCROLL_STEP
    game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP))
    game.handle_event(pygame.event.Event(pygame.MOUSEWHEEL, x=0, y=1))
    assert game._menu.scroll == 0


def test_scrolling_does_nothing_on_the_other_pages(game):
    show(game, PAGE_MODE)

    game.handle_event(pygame.event.Event(pygame.MOUSEWHEEL, x=0, y=-1))

    assert game._menu.scroll == 0


def test_every_menu_page_draws(game):
    for page in (PAGE_MAIN, PAGE_MODE, PAGE_CREDITS, PAGE_THANKS):
        show(game, page)
        game.update()
        game.draw()  # must not raise


def test_step_intro_single_player_only_moves_p1(game):
    game._world.two_players = False
    p1_y_before, p2_y_before = game._p1.y, game._p2.y

    game._step_intro()

    # intro_jump() always advances y (gravity/velocity integration runs
    # unconditionally once called), so an untouched p2 is proof it was
    # never called for this player in single-player mode.
    assert game._p1.y != p1_y_before
    assert game._p2.y == p2_y_before


def test_step_intro_two_player_seq_2_moves_both_players_every_call(game):
    game._world.two_players = True
    game._intro_seq = 2
    p1_y_before, p2_y_before = game._p1.y, game._p2.y

    game._step_intro()

    assert game._p1.y != p1_y_before
    assert game._p2.y != p2_y_before


def test_step_intro_two_player_seq_1_holds_p2_until_p1_descends_past_the_threshold(
    game,
):
    game._world.two_players = True
    game._intro_seq = 1
    game._intro_flag = False
    game._p1.y = settings.FLOOR_Y
    game._p2.y = settings.FLOOR_Y
    p2_y_before = game._p2.y

    game._step_intro()  # p1 still above the gate (FLOOR_Y - 150) -- p2 must not move yet
    assert game._p2.y == p2_y_before
    assert game._intro_flag is False

    game._p1.y = settings.FLOOR_Y - 150  # force p1 past the gate
    game._step_intro()

    assert game._intro_flag is True
    assert game._p2.y != p2_y_before


def test_step_intro_two_player_seq_3_holds_p1_until_p2_descends_past_the_threshold(
    game,
):
    game._world.two_players = True
    game._intro_seq = 3
    game._intro_flag = False
    game._p1.y = settings.FLOOR_Y
    game._p2.y = settings.FLOOR_Y
    p1_y_before = game._p1.y

    game._step_intro()  # p2 still above the gate (FLOOR_Y - 150) -- p1 must not move yet
    assert game._p1.y == p1_y_before
    assert game._intro_flag is False

    game._p2.y = settings.FLOOR_Y - 150  # force p2 past the gate
    game._step_intro()

    assert game._intro_flag is True
    assert game._p1.y != p1_y_before


def test_update_menu_advances_the_countdown_by_one(game):
    game._state = Game.STATE_MENU
    game._countdown = 10

    game._update_menu()

    assert game._countdown == 11
    assert game._state == Game.STATE_MENU


def test_update_menu_transitions_to_level_select_once_countdown_reaches_60(game):
    game._state = Game.STATE_MENU
    game._countdown = 59

    game._update_menu()

    assert game._countdown == 60
    assert game._state == Game.STATE_LEVEL_SELECT
    game._state = (
        Game.STATE_MENU
    )  # restore, so later tests get their expected starting state


def test_handle_level_select_event_selecting_a_level_enters_game(game):
    game._state = Game.STATE_LEVEL_SELECT
    rect = game._renderer.level_card_rect(1)

    click(game, rect.center)

    assert game._current_level == 1
    assert game._state == Game.STATE_GAME
    assert len(game._world.platforms) == len(settings.LEVELS[1]["platforms"])


def test_single_player_mode_binds_an_ai_handler_to_p2(game):
    # Explicit rather than relying on leftover two_players state from an
    # earlier test -- _reset_players() only attaches AIInputHandler when
    # two_players is False *at the moment it runs* (see _make_player()).
    game._state = Game.STATE_LEVEL_SELECT
    game._world.two_players = False

    click(
        game, game._renderer.level_card_rect(0).center
    )  # -> _reset_players() -> _enter_game()

    assert isinstance(game._p2._input, AIInputHandler)
    assert game._p2._input._self is game._p2
    assert game._p2._input._target is game._p1


def test_update_level_select_switches_the_cursor_state_when_hovering_a_card(game):
    game._state = Game.STATE_LEVEL_SELECT
    rect = game._renderer.level_card_rect(0)

    game.mouse.position = rect.center
    game._update_level_select()
    assert game._cursor.state == CLICK

    game.mouse.position = (0, 0)  # outside every card
    game._update_level_select()
    assert game._cursor.state == NORMAL


def test_entering_the_game_resets_the_cursor_to_the_arrow(game):
    game._cursor.set_state(CLICK)

    game._enter_game()

    assert game._cursor.state == NORMAL


def test_update_game_awards_a_point_and_starts_a_new_round_on_a_kill(game, monkeypatch):
    game._state = Game.STATE_GAME
    game._enter_game()
    winner = game._p1
    start_score = winner.score

    monkeypatch.setattr(game._combat, "resolve", lambda vampire, peasant: winner)
    monkeypatch.setattr(
        game._combat,
        "begin_round",
        lambda vampire, p1, p2: (game._vampire, game._peasant),
    )

    game._update_game()

    assert winner.score == start_score + 1


def test_on_exit_request_from_level_select_returns_to_the_menu(game):
    game._state = Game.STATE_LEVEL_SELECT
    game._countdown = 42

    game.on_exit_request()

    assert game._state == Game.STATE_MENU
    assert game._countdown == 100


def test_on_exit_request_from_game_returns_to_the_menu_and_clears_bullets(game):
    game._state = Game.STATE_GAME
    game._world.bullets.append(object())

    game.on_exit_request()

    assert game._state == Game.STATE_MENU
    assert game._world.bullets == []


def test_on_exit_request_from_the_menu_delegates_to_the_real_quit(game, monkeypatch):
    # From STATE_MENU there's nowhere softer to fall back to -- it's really
    # quitting. Application.exit() calls sys.exit(), so it's monkeypatched
    # rather than actually invoked here.
    show(game, PAGE_MAIN)
    calls = []
    monkeypatch.setattr(game, "exit", lambda: calls.append(True))

    game.on_exit_request()

    assert calls == [True]


def test_browser_build_has_no_splash(monkeypatch):
    # The splash decodes video frames on a thread, which the browser build lacks.
    monkeypatch.setattr("util.web.is_web", lambda: True)
    assert Game().splash is None


def test_desktop_build_shows_the_splash():
    assert Game().splash is not None


def _fake_browser(monkeypatch, fullscreen):
    from types import SimpleNamespace
    from unittest.mock import Mock

    document = SimpleNamespace(
        fullscreenElement=object() if fullscreen else None,
        documentElement=SimpleNamespace(requestFullscreen=Mock()),
        exitFullscreen=Mock(),
    )
    monkeypatch.setattr("util.web.is_web", lambda: True)
    monkeypatch.setattr("util.web._window", lambda: SimpleNamespace(document=document))
    return document


@pytest.mark.parametrize("fullscreen", [False, True])
def test_f11_toggles_browser_fullscreen(game, monkeypatch, fullscreen):
    document = _fake_browser(monkeypatch, fullscreen)
    game._handle_core_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F11))
    entered = document.documentElement.requestFullscreen
    assert entered.called is (not fullscreen)
    assert document.exitFullscreen.called is fullscreen


def test_f11_cycles_window_modes_on_desktop(game, monkeypatch):
    modes = []
    monkeypatch.setattr(
        "pygamine.Application.cycle_window_mode",
        lambda self, step=1: modes.append(step),
    )
    game._handle_core_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_F11))
    assert modes == [1]


@pytest.mark.parametrize("fullscreen", [False, True])
def test_is_fullscreen_reads_the_page(monkeypatch, fullscreen):
    from util import web

    _fake_browser(monkeypatch, fullscreen)
    assert web.is_fullscreen() is fullscreen


def test_window_icon_file_exists_and_is_small_square():
    icon = pygame.image.load(settings.WINDOW_ICON)
    assert icon.get_width() == icon.get_height() == 64
