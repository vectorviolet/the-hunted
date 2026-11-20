import pygame

from countdown import END_FRAME, ORANGE, POSITION, RING_OUTER, RING_WIDTH, SIZE
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


def test_construction_loads_the_expected_button_counts():
    menu = make_menu()

    assert menu._start_btn.get_size() == (310, 100)
    assert len(menu._btn_1p) == 3
    assert len(menu._btn_2p) == 3
    assert all(f.get_size() == (212, 44) for f in menu._btn_1p + menu._btn_2p)


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

    for buttons in (menu._btn_1p, menu._btn_2p):
        images = {pygame.image.tobytes(b, "RGBA") for b in buttons}
        assert len(images) == 3
    assert pygame.image.tobytes(menu._btn_1p[0], "RGBA") != pygame.image.tobytes(
        menu._btn_2p[0], "RGBA"
    )  # the labels differ


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


def _ring_pixel(surface):
    x = POSITION[0] + SIZE // 2 + round(RING_OUTER - RING_WIDTH / 2)
    return tuple(surface.get_at((x, POSITION[1] + SIZE // 2)))[:3]


def test_draw_paints_the_countdown_only_while_it_runs(world, input_handler):
    menu = make_menu()
    p1 = Player(world, (100, 100), input_handler)

    drawn = pygame.Surface((800, 600))
    menu.draw(drawn, countdown=30, p1=p1)  # digit 1, ring filled on the right
    assert _ring_pixel(drawn) == ORANGE

    for countdown in (0, END_FRAME, 100):
        idle = pygame.Surface((800, 600))
        menu.draw(idle, countdown=countdown, p1=p1)
        assert _ring_pixel(idle) != ORANGE


def test_draw_late_countdown_draws_go(world, input_handler):
    menu = make_menu()
    surface = pygame.Surface((800, 600))
    p1 = Player(world, (100, 100), input_handler)

    menu.draw(surface, countdown=55, p1=p1)  # must not raise


def test_randomize_background_delegates_to_the_background(world):
    menu = make_menu()
    surface = menu._background.surface

    menu.randomize_background()

    assert menu._background.surface is surface  # re-baked in place
