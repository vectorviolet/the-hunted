"""The level layouts fit the 960x540 canvas and can be played: every platform can be reached
with the real jump, and two AIs on each level keep finishing rounds."""

import random

import pytest

import settings
from combat import CombatSystem
from entities import Player, level_platforms
from input_handler import AIInputHandler
from renderer import TAG_RISE, TOP_HUD_HEIGHT
from world import GameWorld

W, H = settings.VIRTUAL_W, settings.VIRTUAL_H
LEVEL_IDS = range(len(settings.LEVELS))
APEX_MARGIN = 12  # a platform must be this far below the jump's apex to land on it
HUD_MARGIN = 6  # px between the HUD and a standing player's role tag
STAND_HEIGHT = settings.GROUND_Y - int(
    settings.FLOOR_Y
)  # sprite top above its platform (60)


@pytest.mark.parametrize("level", LEVEL_IDS)
def test_platforms_sit_inside_the_canvas_above_the_ground(level):
    for (x, y), w, h in settings.LEVELS[level]["platforms"]:
        assert 0 <= x and x + w <= W
        assert y + h <= settings.GROUND_Y  # not inside the ground
        assert y % 10 == 0  # "platform y must end in 0" (settings.py)


@pytest.mark.parametrize("level", LEVEL_IDS)
def test_a_player_standing_on_any_platform_clears_the_top_hud(level):
    """The role tag sits TAG_RISE above the sprite, and the sprite stands STAND_HEIGHT above the
    platform: the tag must be below the HUD with a margin."""
    for (x, y), _, _ in settings.LEVELS[level]["platforms"]:
        tag_top = y - STAND_HEIGHT - TAG_RISE
        assert tag_top >= TOP_HUD_HEIGHT + HUD_MARGIN, (
            settings.LEVELS[level]["name"],
            y,
        )


@pytest.mark.parametrize("level", LEVEL_IDS)
def test_the_tiers_are_evenly_spaced_between_the_ground_and_the_top(level):
    ys = sorted(
        {y for (_, y), _, _ in settings.LEVELS[level]["platforms"]}
        | {settings.GROUND_Y},
        reverse=True,
    )
    steps = [a - b for a, b in zip(ys, ys[1:])]
    assert (
        max(steps) <= 150
    )  # the steps Classic always had; under the jump's 189 px apex
    assert max(steps) - min(steps) <= 40  # no tier is squeezed against another


@pytest.mark.parametrize("level", LEVEL_IDS)
def test_platforms_span_the_whole_width(level):
    platforms = settings.LEVELS[level]["platforms"]

    assert min(x for (x, _), _, _ in platforms) == 0
    assert max(x + w for (x, _), w, _ in platforms) == W


@pytest.mark.parametrize("level", LEVEL_IDS)
def test_platform_layouts_are_left_right_symmetric(level):
    spans = sorted(
        (x, x + w, y) for (x, y), w, _ in settings.LEVELS[level]["platforms"]
    )
    mirrored = sorted((W - end, W - start, y) for start, end, y in spans)
    # (the Arena's two low platforms sit 60 px in from the edges: still symmetric)
    assert spans == mirrored


def _jump_arc(role: str, input_handler) -> list[tuple[float, float]]:
    """(horizontal travel, height above the start) per frame of a running jump, from the real
    physics, until the player lands again."""
    world = GameWorld(W, H)
    player = Player(world, (400, settings.FLOOR_Y), input_handler)
    player.be_vampire() if role == "vampire" else player.be_peasant()
    input_handler.right = True
    input_handler.jump = True
    player.vel_x = player.mov_speed
    x0 = player.x
    arc = []
    for _ in range(200):
        player.update()
        arc.append((player.x - x0, settings.FLOOR_Y - player.y))
        input_handler.jump = False
        if player.on_ground:
            break
    assert player.on_ground, "the jump never ended"
    return arc


def _reach(arc, rise: float) -> float | None:
    """Horizontal distance covered by the time a jump comes back down through `rise` px
    above its start; None when it never gets that high."""
    apex = max(height for _, height in arc)
    if rise >= apex - APEX_MARGIN:
        return None
    peak = max(range(len(arc)), key=lambda i: arc[i][1])
    for dx, height in arc[peak:]:
        if height <= rise:
            return dx
    return arc[-1][0]


def _gap(a: tuple[int, int], b: tuple[int, int]) -> float:
    """Horizontal gap between two spans (start, end) on the screen that wraps around."""
    direct = max(a[0] - b[1], b[0] - a[1], 0)
    wrapped = max(a[0] + W - b[1], b[0] + W - a[1], 0)
    wrapped2 = max(a[0] - b[1] - W, b[0] - a[1] - W, 0)
    return min(direct, wrapped, wrapped2)


@pytest.mark.parametrize("role", ["peasant", "vampire"])
@pytest.mark.parametrize("level", LEVEL_IDS)
def test_every_platform_can_be_reached_from_the_ground_with_the_real_jump(
    level, role, input_handler
):
    arc = _jump_arc(role, input_handler)
    ground = ("ground", (0, W), settings.GROUND_Y)
    surfaces = [ground] + [
        (f"platform {i}", (x, x + w), y)
        for i, ((x, y), w, _) in enumerate(settings.LEVELS[level]["platforms"])
    ]
    reached = {"ground"}
    changed = True
    while changed:
        changed = False
        for name, span, y in surfaces:
            if name in reached:
                continue
            for src_name, src_span, src_y in surfaces:
                if src_name not in reached:
                    continue
                gap = _gap(span, src_span)
                rise = src_y - y
                if rise <= 0:  # a drop (or level): walking off the edge and falling
                    ok = gap <= (_reach(arc, 0) or 0) + 1
                else:
                    reach = _reach(arc, rise)
                    ok = reach is not None and gap <= reach
                if ok:
                    reached.add(name)
                    changed = True
                    break
    assert reached == {name for name, _, _ in surfaces}, (
        f"unreachable on {settings.LEVELS[level]['name']}: "
        f"{sorted({n for n, _, _ in surfaces} - reached)}"
    )


def test_the_jump_arc_is_what_the_layouts_were_designed_for(input_handler):
    arc = _jump_arc("peasant", input_handler)

    assert max(height for _, height in arc) == pytest.approx(196, abs=10)
    assert 250 < arc[-1][0] < 300  # a full-speed jump covers about 280 px


def _play(level: int, seed: int, frames: int):
    """Two AIs against each other on `level`; returns (round lengths, longest still stretch
    of the vampire in frames)."""
    random.seed(seed)
    world = GameWorld(W, H)
    world.platforms = level_platforms(level)
    combat = CombatSystem(world)
    p1 = Player(world, (600, settings.FLOOR_Y), AIInputHandler())
    p2 = Player(world, (300, settings.FLOOR_Y), AIInputHandler())
    p1._input.bind(p1, p2)
    p2._input.bind(p2, p1)
    p1.be_peasant()
    p2.be_peasant()
    vampire, peasant = combat.begin_round(p1, p1, p2)
    lengths, start, still, longest_still, last = [], 0, 0, 0, None
    for frame in range(frames):
        p1.update()
        p2.update()
        pos = (round(vampire.x), round(vampire.y))
        still = still + 1 if pos == last else 0
        longest_still, last = max(longest_still, still), pos
        if combat.resolve(vampire, peasant) is not None:
            lengths.append(frame - start)
            start = frame
            vampire, peasant = combat.begin_round(vampire, p1, p2)
    return lengths, longest_still


@pytest.mark.parametrize("level", LEVEL_IDS)
def test_two_ais_keep_finishing_rounds_on_every_level(level):
    lengths, longest_still = _play(level, seed=3, frames=8000)

    assert len(lengths) >= 15  # rounds keep ending
    assert max(lengths) < 4000  # none drags on (the longest seen is about 2300 frames)
    assert longest_still < 120  # the chaser is never stuck in place
