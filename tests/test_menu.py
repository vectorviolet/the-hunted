import pygame

import settings
from buttons import BTN_HOVER, BTN_NORMAL, BTN_PRESSED, LABEL_OFFSET, make_button
from countdown import END_FRAME
from cursor import CLICK, CLICK2, NORMAL
from entities import Player
from menu import Menu


class FakeCursor:
    """Records the states Menu asks for; a real Cursor's images are irrelevant to
    Menu's own hover/click-state logic under test here."""

    def __init__(self):
        self.state = NORMAL

    def set_state(self, state):
        self.state = state


def make_menu():
    return Menu(800, 600, FakeCursor())


def test_construction_builds_every_button_in_all_three_states():
    menu = make_menu()

    for buttons, size in (
        (menu._start_btn, (310, 100)),
        (menu._btn_1p, (212, 44)),
        (menu._btn_2p, (212, 44)),
    ):
        assert set(buttons) == {BTN_NORMAL, BTN_PRESSED, BTN_HOVER}
        assert all(image.get_size() == size for image in buttons.values())


def test_update_button_state_hover_without_press():
    menu = make_menu()

    menu.update_button_state("1p", hovered=True, pressed=False)

    assert menu._btn_1p_hover is True
    assert menu._btn_1p_click is False


def test_update_button_state_press_while_hovering():
    menu = make_menu()

    menu.update_button_state("1p", hovered=True, pressed=True)

    assert menu._btn_1p_hover is False
    assert menu._btn_1p_click is True


def test_update_button_state_pressed_flag_is_ignored_when_not_hovering():
    menu = make_menu()

    menu.update_button_state("start", hovered=False, pressed=True)

    assert menu._btn_start_hover is False
    assert menu._btn_start_click is False


def test_draw_at_full_countdown_shows_the_start_screen_and_hovered_cursor(
    world, input_handler
):
    menu = make_menu()
    menu.update_button_state("1p", hovered=True, pressed=False)
    surface = pygame.Surface((800, 600))
    p1 = Player(world, (100, 100), input_handler)

    menu.draw(surface, countdown=100, p1=p1)

    assert menu.cursor.state == CLICK


def test_draw_switches_the_cursor_with_the_button_state(world, input_handler):
    menu = make_menu()
    surface = pygame.Surface((800, 600))
    p1 = Player(world, (100, 100), input_handler)

    menu.update_button_state("2p", hovered=True, pressed=True)
    menu.draw(surface, countdown=100, p1=p1)
    assert menu.cursor.state == CLICK2

    menu.update_button_state("2p", hovered=False, pressed=False)
    menu.draw(surface, countdown=100, p1=p1)
    assert menu.cursor.state == NORMAL


def test_the_three_button_states_look_different():
    menu = make_menu()

    for buttons in (menu._start_btn, menu._btn_1p, menu._btn_2p):
        images = {pygame.image.tobytes(b, "RGBA") for b in buttons.values()}
        assert len(images) == 3
    assert pygame.image.tobytes(
        menu._btn_1p[BTN_NORMAL], "RGBA"
    ) != pygame.image.tobytes(menu._btn_2p[BTN_NORMAL], "RGBA")  # the labels differ


def test_draw_supports_single_player_with_no_p2(world, input_handler):
    menu = make_menu()
    surface = pygame.Surface((800, 600))
    p1 = Player(world, (100, 100), input_handler)

    menu.draw(surface, countdown=100, p1=p1, p2=None)  # must not raise


def test_draw_with_two_players(world, input_handler):
    menu = make_menu()
    surface = pygame.Surface((800, 600))
    p1 = Player(world, (100, 100), input_handler)
    p2 = Player(world, (200, 100), input_handler)

    menu.draw(surface, countdown=100, p1=p1, p2=p2)  # must not raise


def test_draw_mid_countdown_draws_the_countdown(world, input_handler):
    menu = make_menu()
    surface = pygame.Surface((800, 600))
    p1 = Player(world, (100, 100), input_handler)

    menu.draw(surface, countdown=30, p1=p1)  # must not raise, no start screen drawn


def test_draw_paints_the_countdown_only_while_it_runs(world, input_handler):
    menu = make_menu()
    p1 = Player(world, (100, 100), input_handler)

    def frame(countdown):
        surface = pygame.Surface((800, 600))
        menu.draw(surface, countdown=countdown, p1=p1)
        return pygame.image.tobytes(surface, "RGB")

    bare = frame(0)  # running, but no glyph yet: the buttons are gone, nothing else
    assert frame(END_FRAME) == bare  # no glyph once it is over either
    assert frame(100) != bare  # idle: the start buttons
    assert frame(30) != bare  # a glyph is on screen
    assert frame(20) != frame(50)  # and it changes as the countdown runs


def test_draw_late_countdown_draws_go(world, input_handler):
    menu = make_menu()
    surface = pygame.Surface((800, 600))
    p1 = Player(world, (100, 100), input_handler)

    menu.draw(surface, countdown=55, p1=p1)  # must not raise


def test_cursor_goes_back_to_normal_once_the_countdown_runs(world, input_handler):
    menu = make_menu()
    surface = pygame.Surface((800, 600))
    p1 = Player(world, (100, 100), input_handler)
    menu.update_button_state("start", hovered=True, pressed=True)
    menu.draw(surface, countdown=100, p1=p1)
    assert menu.cursor.state == CLICK2

    menu.draw(surface, countdown=10, p1=p1)

    assert menu.cursor.state == NORMAL


def test_a_pressed_buttons_label_sits_lower_than_a_raised_ones():
    def label_top(state):
        # The label is drawn in BONE; the first row with a BONE pixel inside the face.
        image = make_button(state, (212, 44), "1 PLAYER", 24)
        rows = [
            y
            for y in range(10, 34)
            if any(image.get_at((x, y))[:3] == settings.BONE for x in range(40, 170))
        ]
        return rows[0]

    assert label_top(BTN_PRESSED) == label_top(BTN_NORMAL) + LABEL_OFFSET
