"""The credits page's text is built from assets/SOURCES.yaml (by scripts/gen_credits.py,
into src/credits_data.py), grouped like CREDITS.md. The game itself imports no YAML library."""

import importlib.util
import os
import subprocess
import sys
from pathlib import Path

import credits

ROOT = Path(__file__).resolve().parent.parent
_spec = importlib.util.spec_from_file_location(
    "gen_credits", ROOT / "scripts" / "gen_credits.py"
)
assert _spec is not None and _spec.loader is not None
gen_credits = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen_credits)

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
    return dict(gen_credits.credit_sections({"packs": PACKS, "files": files}))


def test_the_sections_come_in_a_fixed_order_with_the_game_first_and_the_engine_last():
    files = {
        "fonts/a.ttf": {"source": "font-pack"},
        "images/a.png": {"source": "art-pack"},
        "sounds/a.ogg": {"source": "sfx-pack"},
        "sounds/b.ogg": {"source": "song-pack"},
    }

    result = gen_credits.credit_sections({"packs": PACKS, "files": files})

    assert [heading for heading, _ in result] == [
        "GAME",
        "MUSIC",
        "SOUNDS",
        "ART",
        "FONTS",
        "ENGINE",
    ]
    assert result[0] == ("GAME", ["VectorViolet"])
    assert result[-1] == ("ENGINE", list(gen_credits.ENGINE_LINES))


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

    assert result == {
        "GAME": ["VectorViolet"],
        "ENGINE": list(gen_credits.ENGINE_LINES),
    }


def test_the_generated_credits_match_sources_yaml():
    # Fails when SOURCES.yaml changed and scripts/gen_credits.py wasn't run.
    assert credits.load_credit_sections() == gen_credits.credit_sections(
        gen_credits.load_sources()
    )


def test_the_real_credits_cover_every_pack_in_sources_yaml():
    packs = gen_credits.load_sources()["packs"]
    sections = dict(credits.load_credit_sections())
    lines = [line for found in sections.values() for line in found]

    for pack in packs.values():
        assert any(line.startswith(pack["name"]) for line in lines), pack["name"]
    assert sections["GAME"] == ["VectorViolet"]


def test_the_web_game_boots_and_shows_the_credits_without_a_yaml_library():
    # The browser build has no PyYAML: nothing the game imports may need it.
    blocker = (
        "import sys\n"
        "class Block:\n"
        "    def find_spec(self, name, path=None, target=None):\n"
        "        if name.split('.')[0] == 'yaml':\n"
        "            raise ModuleNotFoundError(name)\n"
        "sys.meta_path.insert(0, Block())\n"
        "sys.path[:0] = ['src', 'src/pygamine']\n"
        "from util import web\n"
        "web.is_web = lambda: True\n"  # the browser build: no splash screen
        "import game\n"
        "g = game.Game()\n"
        "g._menu.go_to('credits')\n"
        "g.update()\n"
        "g.draw()\n"
        "assert 'yaml' not in sys.modules\n"
    )
    env = {**os.environ, "SDL_VIDEODRIVER": "dummy", "SDL_AUDIODRIVER": "dummy"}

    result = subprocess.run(
        [sys.executable, "-c", blocker],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
