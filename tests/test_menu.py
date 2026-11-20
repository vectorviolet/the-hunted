import pygame
import pytest

import settings
from buttons import BTN_HOVER, BTN_NORMAL, BTN_PRESSED, LABEL_OFFSET, make_button
from countdown import END_FRAME
from cursor import CLICK, CLICK2, NORMAL
from entities import Player
from menu import (
    BUTTONS,
    CREDITS_VIEW,
    IDLE,
    PAGE_CREDITS,
    PAGE_MAIN,
    PAGE_MODE,
    PANELS,
    SCROLL_STEP,
    Menu,
    wrap_words,
)


class FakeCursor:
    """Records the states Menu asks for; a real Cursor's images are irrelevant to
    Menu's own hover/click-state logic under test here."""

    def __init__(self):
        self.state = NORMAL

    def set_state(self, state):
        self.state = state


def make_menu(page=PAGE_MAIN):
    menu = Menu(960, 540, FakeCursor())
    menu.go_to(page)
    return menu


def frame(menu, world, input_handler, countdown=IDLE):
    surface = pygame.Surface((960, 540))
    p1 = Player(world, (100, 100), input_handler)
    menu.draw(surface, countdown=countdown, p1=p1)
    return pygame.image.tobytes(surface, "RGB")


def test_every_button_exists_in_all_three_states():
    menu = make_menu()

    for page, buttons in BUTTONS.items():
        for name, (_, rect) in buttons.items():
            images = menu._buttons[(page, name)]
            assert set(images) == {BTN_NORMAL, BTN_PRESSED, BTN_HOVER}
            assert all(image.get_size() == rect.size for image in images.values())


@pytest.mark.parametrize("page", list(BUTTONS))
def test_every_button_fits_the_canvas_and_none_overlap(page):
    canvas = pygame.Rect(0, 0, 960, 540)
    rects = [rect for _, rect in BUTTONS[page].values()]

    assert all(canvas.contains(rect) for rect in rects)
    assert not any(
        a.colliderect(b) for i, a in enumerate(rects) for b in rects[i + 1 :]
    )


@pytest.mark.parametrize("page", list(PANELS))
def test_a_pages_buttons_sit_inside_its_panel(page):
    assert all(PANELS[page].contains(rect) for _, rect in BUTTONS[page].values())


def test_the_main_menu_opens_with_play_credits_and_exit():
    menu = Menu(960, 540, FakeCursor())

    assert menu.page == PAGE_MAIN
    assert list(menu.button_rects()) == ["play", "credits", "exit"]


def test_button_at_finds_the_button_under_the_mouse():
    menu = make_menu(PAGE_MODE)

    for name, rect in menu.button_rects().items():
        assert menu.button_at(rect.center) == name
    assert menu.button_at((0, 0)) is None


def test_update_pointer_hover_without_press():
    menu = make_menu()

    menu.update_pointer(menu.button_rects()["play"].center, pressed=False)

    assert menu._hover == "play"
    assert menu._pressed is None


def test_update_pointer_press_while_hovering():
    menu = make_menu()

    menu.update_pointer(menu.button_rects()["play"].center, pressed=True)

    assert menu._hover is None
    assert menu._pressed == "play"


def test_update_pointer_off_every_button_clears_both():
    menu = make_menu()
    menu.update_pointer(menu.button_rects()["play"].center, pressed=False)

    menu.update_pointer((0, 0), pressed=True)

    assert menu._hover is None
    assert menu._pressed is None


def test_going_to_another_page_clears_the_hover_and_the_scroll():
    menu = make_menu(PAGE_CREDITS)
    menu.scroll_by(SCROLL_STEP)
    menu.update_pointer(menu.button_rects()["back"].center, pressed=False)

    menu.go_to(PAGE_MAIN)

    assert menu.scroll == 0
    assert menu._hover is None


def test_the_credits_are_taller_than_the_view_so_they_scroll():
    assert make_menu(PAGE_CREDITS).max_scroll > 0


def test_scrolling_stays_between_the_top_and_the_end_of_the_text():
    menu = make_menu(PAGE_CREDITS)

    menu.scroll_by(-500)
    assert menu.scroll == 0
    menu.scroll_by(SCROLL_STEP)
    assert menu.scroll == SCROLL_STEP
    menu.scroll_by(100_000)
    assert menu.scroll == menu.max_scroll
    assert menu._credits.get_height() - menu.scroll == CREDITS_VIEW.height


def test_text_that_fits_does_not_scroll():
    menu = make_menu(PAGE_CREDITS)
    menu._credits = pygame.Surface((CREDITS_VIEW.width, CREDITS_VIEW.height))

    menu.scroll_by(SCROLL_STEP)

    assert menu.max_scroll == 0
    assert menu.scroll == 0


def test_scrolling_moves_the_credits_on_screen(world, input_handler):
    menu = make_menu(PAGE_CREDITS)
    top = frame(menu, world, input_handler)

    menu.scroll_by(SCROLL_STEP * 3)

    assert frame(menu, world, input_handler) != top


def test_wrap_words_breaks_at_spaces_to_fit_the_width():
    font = pygame.font.Font(settings.UI_FONT, 16)
    text = "one two three four five six seven eight nine ten"
    width = font.size("one two three")[0] + 1

    lines = wrap_words(text, font, width)

    assert " ".join(lines) == text
    assert len(lines) > 1
    assert all(font.size(line)[0] <= width for line in lines)


def test_wrap_words_keeps_a_word_that_is_too_long_whole():
    font = pygame.font.Font(settings.UI_FONT, 16)

    assert wrap_words("supercalifragilistic", font, 10) == ["supercalifragilistic"]


def test_draw_at_full_countdown_shows_the_page_and_the_hovered_cursor(
    world, input_handler
):
    menu = make_menu()
    menu.update_pointer(menu.button_rects()["play"].center, pressed=False)
    surface = pygame.Surface((960, 540))
    p1 = Player(world, (100, 100), input_handler)

    menu.draw(surface, countdown=IDLE, p1=p1)

    assert menu.cursor.state == CLICK


def test_draw_switches_the_cursor_with_the_button_state(world, input_handler):
    menu = make_menu()
    surface = pygame.Surface((960, 540))
    p1 = Player(world, (100, 100), input_handler)
    center = menu.button_rects()["credits"].center

    menu.update_pointer(center, pressed=True)
    menu.draw(surface, countdown=IDLE, p1=p1)
    assert menu.cursor.state == CLICK2

    menu.update_pointer((0, 0), pressed=False)
    menu.draw(surface, countdown=IDLE, p1=p1)
    assert menu.cursor.state == NORMAL


def test_the_three_button_states_look_different():
    menu = make_menu()

    for images in menu._buttons.values():
        rendered = {pygame.image.tobytes(b, "RGBA") for b in images.values()}
        assert len(rendered) == 3


def test_every_page_looks_different(world, input_handler):
    shots = {page: frame(make_menu(page), world, input_handler) for page in BUTTONS}

    assert len(set(shots.values())) == len(BUTTONS)


def test_draw_supports_single_player_with_no_p2(world, input_handler):
    menu = make_menu()
    surface = pygame.Surface((960, 540))
    p1 = Player(world, (100, 100), input_handler)

    menu.draw(surface, countdown=IDLE, p1=p1, p2=None)  # must not raise


def test_draw_with_two_players_on_every_page(world, input_handler):
    surface = pygame.Surface((960, 540))
    p1 = Player(world, (100, 100), input_handler)
    p2 = Player(world, (200, 100), input_handler)

    for page in BUTTONS:
        make_menu(page).draw(surface, countdown=IDLE, p1=p1, p2=p2)  # must not raise


def test_draw_mid_countdown_draws_the_countdown(world, input_handler):
    menu = make_menu()
    surface = pygame.Surface((960, 540))
    p1 = Player(world, (100, 100), input_handler)

    menu.draw(surface, countdown=30, p1=p1)  # must not raise, no page drawn


def test_draw_paints_the_countdown_only_while_it_runs(world, input_handler):
    menu = make_menu()

    def shot(countdown):
        return frame(menu, world, input_handler, countdown)

    bare = shot(0)  # running, but no glyph yet: the page is gone, nothing else
    assert shot(END_FRAME) == bare  # no glyph once it is over either
    assert shot(IDLE) != bare  # idle: the page
    assert shot(30) != bare  # a glyph is on screen
    assert shot(20) != shot(50)  # and it changes as the countdown runs


def test_cursor_goes_back_to_normal_once_the_countdown_runs(world, input_handler):
    menu = make_menu()
    surface = pygame.Surface((960, 540))
    p1 = Player(world, (100, 100), input_handler)
    menu.update_pointer(menu.button_rects()["play"].center, pressed=True)
    menu.draw(surface, countdown=IDLE, p1=p1)
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
