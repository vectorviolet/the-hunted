import pygame
import pytest

import settings
from background import load_background
from entities import Platform, Player, Projectile
from renderer import CARD_LIFT, GameRenderer


@pytest.fixture
def renderer(world):
    world.platforms = [
        Platform(loc, w, h) for loc, w, h in settings.LEVELS[0]["platforms"]
    ]
    return GameRenderer(pygame.Surface((world.window_w, world.window_h)), world)


def test_level_card_rect_lays_cards_out_left_to_right_centered_in_the_window(renderer):
    assert renderer.level_card_rect(0) == pygame.Rect(95, 165, 240, 210)
    assert renderer.level_card_rect(1) == pygame.Rect(360, 165, 240, 210)
    assert renderer.level_card_rect(2) == pygame.Rect(625, 165, 240, 210)


def score_surfaces():
    font = pygame.font.SysFont(None, 20)
    return [
        font.render("P1   0", True, settings.WHITE),
        font.render("P2   0", True, settings.WHITE),
    ]


def test_draw_game_with_two_players_and_a_bullet_does_not_raise(
    renderer, world, input_handler
):
    p1 = Player(world, (100, settings.FLOOR_Y), input_handler)
    p2 = Player(world, (200, settings.FLOOR_Y), input_handler)
    p1.be_peasant()
    p2.be_vampire()
    world.bullets.append(Projectile(50, 50, settings.BULLET_RADIUS, settings.BLACK, 1))

    renderer.draw_game(
        p1, p2, vampire=p2, current_level=0, score_surfs=score_surfaces()
    )


def test_draw_game_single_player_with_no_p2_does_not_raise(
    renderer, world, input_handler
):
    p1 = Player(world, (100, settings.FLOOR_Y), input_handler)
    p1.be_peasant()

    renderer.draw_game(
        p1, None, vampire=p1, current_level=0, score_surfs=score_surfaces()
    )


def test_draw_level_select_does_not_raise_hovered_or_not(renderer):
    renderer.draw_level_select((0, 0))  # no card hovered
    renderer.draw_level_select(renderer.level_card_rect(1).center)  # hovering card 1


def test_health_bar_color_tiers_by_hp_fraction(renderer, world, input_handler):
    p1 = Player(world, (100, settings.FLOOR_Y), input_handler)
    p1.be_peasant()
    ix, iy = int(p1.x), int(p1.y)
    bar_x = ix + (p1.width - 52) // 2
    bar_y = iy - 12
    sample = (bar_x + 1, bar_y + 1)  # inside the fill for every tier tested below

    p1.hp = p1.max_hp  # > 50% -> green
    renderer._draw_health_bar(p1, ix, iy)
    assert renderer._window.get_at(sample)[:3] == settings.HP_GREEN

    p1.hp = int(p1.max_hp * 0.4)  # 25%-50% -> yellow
    renderer._draw_health_bar(p1, ix, iy)
    assert renderer._window.get_at(sample)[:3] == settings.HP_YELLOW

    p1.hp = int(p1.max_hp * 0.1)  # <= 25% -> red
    renderer._draw_health_bar(p1, ix, iy)
    assert renderer._window.get_at(sample)[:3] == settings.HP_RED


@pytest.mark.parametrize("level", range(len(settings.LEVELS)))
def test_draw_game_paints_the_levels_own_backdrop(
    renderer, world, input_handler, level
):
    p1 = Player(world, (100, settings.FLOOR_Y), input_handler)
    p1.be_peasant()

    renderer.draw_game(
        p1, None, vampire=p1, current_level=level, score_surfs=score_surfaces()
    )

    backdrop = load_background(settings.LEVELS[level]["background"], (960, 540))
    # (400, 100) has no platform, HUD or player on it in any level.
    assert renderer._window.get_at((400, 100)) == backdrop.get_at((400, 100))


def test_the_top_hud_plates_have_each_players_edge_color(
    renderer, world, input_handler
):
    p1 = Player(world, (100, settings.FLOOR_Y), input_handler)
    p2 = Player(world, (200, settings.FLOOR_Y), input_handler)
    p1.be_peasant()
    p2.be_vampire()

    renderer.draw_game(
        p1, p2, vampire=p2, current_level=0, score_surfs=score_surfaces()
    )

    assert renderer._window.get_at((0, 0))[:3] == settings.SLATE
    assert renderer._window.get_at((world.window_w - 1, 0))[:3] == settings.CRIMSON


def test_the_role_tag_is_a_plate_over_the_player(renderer, world, input_handler):
    p1 = Player(world, (300, settings.FLOOR_Y), input_handler)
    p1.be_vampire()
    plate = pygame.Rect(0, 0, 10, 10)
    plate.midtop = (300 + p1.width // 2, int(p1.y) - 50)

    renderer.draw_game(
        p1, None, vampire=p1, current_level=0, score_surfs=score_surfaces()
    )

    assert renderer._window.get_at(plate.midtop)[:3] == settings.PLUM


def _count_color(surface, rect, color):
    return sum(
        surface.get_at((x, y))[:3] == color
        for x in range(rect.left, rect.right)
        for y in range(rect.top, rect.bottom)
    )


def test_a_hovered_card_lifts_and_shows_its_hint(renderer):
    card = renderer.level_card_rect(1)
    below = pygame.Rect(card.left, card.bottom + 8, card.width, 30)

    renderer.draw_level_select((0, 0))
    idle_hint = _count_color(renderer._window, below, settings.GOLD)
    renderer.draw_level_select(card.center)
    hover_hint = _count_color(renderer._window, below, settings.GOLD)

    assert idle_hint == 0
    assert hover_hint > 0


def test_each_card_previews_its_own_level(renderer):
    previews = {
        pygame.image.tobytes(renderer._thumb(i, 192), "RGB")
        for i in range(len(settings.LEVELS))
    }

    assert len(previews) == len(settings.LEVELS)
    assert renderer._thumb(0, 192).get_size() == (192, 108)


def test_a_preview_is_cached_per_size(renderer):
    assert renderer._thumb(0, 192) is renderer._thumb(0, 192)
    assert renderer._thumb(0, 80).get_size() == (80, 45)
    assert renderer._thumb(0, 192).get_size() == (192, 108)


def test_the_level_selects_back_button_is_clear_of_the_cards_and_their_hint(renderer):
    back = renderer.back_rect()
    canvas = pygame.Rect(0, 0, 960, 540)

    assert canvas.contains(back)
    for i in range(len(settings.LEVELS)):
        card = renderer.level_card_rect(i)
        assert not back.colliderect(card.inflate(0, 60).move(0, -CARD_LIFT))


def test_the_back_button_changes_with_hover_and_press(renderer):
    back = renderer.back_rect()

    def drawn(pos, pressed=False):
        renderer.draw_level_select(pos, pressed)
        return pygame.image.tobytes(renderer._window.subsurface(back), "RGB")

    idle, hover, pressed = drawn((0, 0)), drawn(back.center), drawn(back.center, True)

    assert len({idle, hover, pressed}) == 3
