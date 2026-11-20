import pygame
import pytest

from entities import Platform, level_platforms
import settings
from pixelart import STRIP_CAP, STRIP_MID, nine_slice, three_slice


def _sheet() -> pygame.Surface:
    """A cap | middle | cap sheet whose three parts are plain, different colors."""
    sheet = pygame.Surface((2 * STRIP_CAP + STRIP_MID, 4), pygame.SRCALPHA)
    sheet.fill((255, 0, 0), (0, 0, STRIP_CAP, 4))
    sheet.fill((0, 255, 0), (STRIP_CAP, 0, STRIP_MID, 4))
    sheet.fill((0, 0, 255), (STRIP_CAP + STRIP_MID, 0, STRIP_CAP, 4))
    return sheet


@pytest.mark.parametrize("width", [2 * STRIP_CAP, 100, 300, 800])
def test_three_slice_keeps_the_caps_and_fills_the_middle(width):
    strip = three_slice(_sheet(), width)

    assert strip.get_size() == (width, 4)
    assert strip.get_at((0, 0))[:3] == (255, 0, 0)
    assert strip.get_at((STRIP_CAP - 1, 3))[:3] == (255, 0, 0)
    assert strip.get_at((width - 1, 0))[:3] == (0, 0, 255)
    assert strip.get_at((width - STRIP_CAP, 3))[:3] == (0, 0, 255)
    middle = {strip.get_at((x, 1))[:3] for x in range(STRIP_CAP, width - STRIP_CAP)}
    assert middle <= {(0, 255, 0)}


def test_three_slice_rejects_a_strip_too_short_for_its_caps():
    with pytest.raises(AssertionError):
        three_slice(_sheet(), 2 * STRIP_CAP - 1)


def test_three_slice_rejects_a_sheet_that_is_not_cap_middle_cap():
    with pytest.raises(AssertionError):
        three_slice(pygame.Surface((50, 4)), 100)


def _frame() -> pygame.Surface:
    """A 30x30 frame: a red border of 10 around a blue middle."""
    frame = pygame.Surface((30, 30), pygame.SRCALPHA)
    frame.fill((255, 0, 0))
    frame.fill((0, 0, 255), (10, 10, 10, 10))
    return frame


@pytest.mark.parametrize("size", [(20, 20), (60, 40), (100, 100)])
def test_nine_slice_keeps_the_corners_and_stretches_the_middle(size):
    result = nine_slice(_frame(), 10, size)

    w, h = size
    assert result.get_size() == size
    for corner in ((0, 0), (w - 1, 0), (0, h - 1), (w - 1, h - 1), (9, 9)):
        assert result.get_at(corner)[:3] == (255, 0, 0)
    if w > 20 and h > 20:
        assert result.get_at((w // 2, h // 2))[:3] == (0, 0, 255)
        assert result.get_at((10, 10))[:3] == (
            0,
            0,
            255,
        )  # the middle starts at the border


def test_nine_slice_rejects_a_size_smaller_than_its_borders():
    with pytest.raises(AssertionError):
        nine_slice(_frame(), 10, (19, 40))


def test_nine_slice_does_not_invent_colors():
    frame = pygame.image.load("assets/images/ui/panel.png").convert_alpha()
    colors = {
        tuple(frame.get_at((x, y)))
        for x in range(frame.get_width())
        for y in range(frame.get_height())
    }

    result = nine_slice(frame, 20, (500, 340))

    seen = {tuple(result.get_at((x, y))) for x in range(500) for y in range(340)}
    assert seen <= colors


@pytest.mark.parametrize("kind", ["platform", "ground"])
@pytest.mark.parametrize("level", range(len(settings.LEVELS)))
def test_every_levels_art_exists_and_has_the_strip_layout(kind, level):
    style = settings.LEVELS[level]["style"]
    sheet = pygame.image.load(f"assets/images/{kind}/{style}.png")

    assert sheet.get_width() == 2 * STRIP_CAP + STRIP_MID


@pytest.mark.parametrize("level", range(len(settings.LEVELS)))
def test_level_platforms_match_the_level_table_and_use_the_levels_art(level):
    platforms = level_platforms(level)

    assert [((p.x, p.y), p.width, p.height) for p in platforms] == [
        (loc, w, h) for loc, w, h in settings.LEVELS[level]["platforms"]
    ]
    for p in platforms:
        assert p.art.get_size() == (p.width, p.height)


def test_a_platform_is_drawn_where_it_is_and_nowhere_else():
    surface = pygame.Surface((400, 200), pygame.SRCALPHA)

    Platform((100, 50), 160, 20, style="arena").draw(surface)

    assert surface.get_bounding_rect() == pygame.Rect(100, 50, 160, 20)


def test_a_platform_is_stretched_to_its_height_when_the_art_is_another_height():
    platform = Platform((0, 0), 160, 40, style="arena")  # the Arena art is 20 px tall

    assert platform.art.get_size() == (160, 40)


def test_the_levels_have_different_platform_art():
    arts = {
        pygame.image.tobytes(Platform((0, 0), 200, 50, style=s).art, "RGBA")
        for s in ("classic", "towers", "arena")
    }
    assert len(arts) == 3
