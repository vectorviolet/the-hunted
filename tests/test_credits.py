"""The credits page's text is built from assets/SOURCES.yaml, grouped like CREDITS.md."""

import credits
import yaml

PACKS = {
    "song-pack": {
        "name": "Song Pack",
        "author": "A. Author",
        "license": "CC0-1.0",
        "used_for": "menu music",
    },
    "sfx-pack": {
        "name": "SFX Pack",
        "author": "B. Maker",
        "license": "CC-BY-3.0",
        "used_for": "jump sound",
    },
    "font-pack": {
        "name": "Fancy Font",
        "author": "C. Typer",
        "license": "OFL-1.1",
        "used_for": "title font",
    },
    "art-pack": {
        "name": "Tile Pack",
        "author": "D. Painter",
        "license": "CC0-1.0",
        "used_for": "tiles",
    },
}


def sections(files):
    return dict(credits.credit_sections({"packs": PACKS, "files": files}))


def test_the_sections_come_in_a_fixed_order_with_the_game_first_and_the_engine_last():
    files = {
        "fonts/a.ttf": {"source": "font-pack"},
        "images/a.png": {"source": "art-pack"},
        "sounds/a.ogg": {"source": "sfx-pack"},
        "sounds/b.ogg": {"source": "song-pack"},
    }

    result = credits.credit_sections({"packs": PACKS, "files": files})

    assert [heading for heading, _ in result] == [
        "GAME",
        "MUSIC",
        "SOUNDS",
        "ART",
        "FONTS",
        "ENGINE",
    ]
    assert result[0] == ("GAME", ["VectorViolet"])
    assert result[-1] == ("ENGINE", list(credits.ENGINE_LINES))


def test_packs_are_grouped_by_where_their_files_live():
    result = sections(
        {
            "fonts/a.ttf": {"source": "font-pack"},
            "images/a.png": {"source": "art-pack"},
            "sounds/a.ogg": {"source": "sfx-pack"},
            "sounds/b.ogg": {"source": "song-pack"},
        }
    )

    assert result["MUSIC"] == ["Song Pack - A. Author (CC0 1.0)"]
    assert result["SOUNDS"] == ["SFX Pack - B. Maker (CC BY 3.0)"]
    assert result["ART"] == ["Tile Pack - D. Painter (CC0 1.0)"]
    assert result["FONTS"] == ["Fancy Font - C. Typer (OFL 1.1)"]


def test_a_pack_with_many_files_is_credited_once():
    result = sections({f"images/{i}.png": {"source": "art-pack"} for i in range(5)})

    assert result["ART"] == ["Tile Pack - D. Painter (CC0 1.0)"]


def test_own_files_are_credited_to_the_developer_and_name_the_ai_tool():
    result = sections(
        {
            "images/a.png": {"source": "own", "generated_with": "Some Tool"},
            "images/b.png": {"source": "own"},
        }
    )

    assert result["ART"] == ["AI-generated with Some Tool", "Made by VectorViolet"]


def test_unknown_files_and_empty_sections_are_left_out():
    result = sections({"images/a.png": {"source": "unknown", "todo": "find it"}})

    assert result == {"GAME": ["VectorViolet"], "ENGINE": list(credits.ENGINE_LINES)}


def test_the_real_credits_cover_every_pack_in_sources_yaml():
    with open(credits.SOURCES_FILE, encoding="utf-8") as file:
        data = yaml.safe_load(file)
    lines = [line for _, found in credits.load_credit_sections() for line in found]

    for pack in data["packs"].values():
        assert any(line.startswith(pack["name"]) for line in lines), pack["name"]
    assert dict(credits.load_credit_sections())["GAME"] == ["VectorViolet"]
