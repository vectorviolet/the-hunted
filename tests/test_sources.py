"""assets/SOURCES.yaml -- where every asset comes from -- is complete and
consistent: every file under assets/ is listed, every listed file exists,
every pack has its license text in licenses/assets/, and CREDITS.md's asset
section is exactly what scripts/gen_credits.py builds from it."""

from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"
LICENSES = ROOT / "licenses" / "assets"

_spec = importlib.util.spec_from_file_location(
    "gen_credits", ROOT / "scripts" / "gen_credits.py"
)
assert _spec is not None and _spec.loader is not None
gen_credits = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(gen_credits)


@pytest.fixture(scope="module")
def sources() -> dict[str, Any]:
    return gen_credits.load_sources()


def _asset_files() -> set[str]:
    """The files git tracks (or would) under assets/, so stray OS files such as
    Thumbs.db or .DS_Store, which .gitignore covers, don't count."""
    out = subprocess.run(
        [
            "git",
            "ls-files",
            "-z",
            "--cached",
            "--others",
            "--exclude-standard",
            "assets",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    return {
        name.removeprefix("assets/")
        for name in out.split("\0")
        if name and name != "assets/SOURCES.yaml"
    }


def test_every_asset_file_is_listed(sources):
    assert sorted(_asset_files() - set(sources["files"])) == []


def test_every_listed_file_exists(sources):
    assert sorted(set(sources["files"]) - _asset_files()) == []


def test_every_source_is_a_known_pack_own_or_unknown(sources):
    allowed = set(sources["packs"]) | {"own", gen_credits.UNKNOWN}
    assert {e["source"] for e in sources["files"].values()} - allowed == set()


def test_every_pack_file_names_its_original(sources):
    for rel, e in sources["files"].items():
        if e["source"] in sources["packs"]:
            assert "original" in e or "composited_from" in e, rel


def test_every_unknown_file_says_what_is_left_to_do(sources):
    for rel, e in sources["files"].items():
        if e["source"] == gen_credits.UNKNOWN:
            assert e.get("todo"), rel


def test_every_pack_has_its_license_text(sources):
    for slug in sources["packs"]:
        text = LICENSES / f"{slug}.txt"
        assert text.is_file() and text.stat().st_size > 0, slug


def test_no_license_text_for_a_pack_that_is_not_used(sources):
    assert {p.stem for p in LICENSES.glob("*.txt")} == set(sources["packs"])


def test_every_pack_license_has_a_link(sources):
    for slug, pack in sources["packs"].items():
        assert pack["license"] in gen_credits.LICENSE_LINKS, slug


def test_credits_md_asset_section_is_generated_from_sources(sources):
    text = gen_credits.CREDITS.read_text(encoding="utf-8")
    assert gen_credits.updated_credits(text, gen_credits.render(sources)) == text, (
        "CREDITS.md is out of date: run scripts/gen_credits.py"
    )


def _fake(files: dict[str, dict[str, str]]) -> dict[str, Any]:
    return {
        "packs": {
            "p": {
                "name": "Pack",
                "author": "Au",
                "url": "https://example.org",
                "license": "CC-BY-3.0",
                "attribution": "Au, with a link",
                "used_for": "things",
            }
        },
        "files": files,
    }


def test_unknown_files_are_listed_as_pending_and_never_credited():
    text = gen_credits.render(
        _fake(
            {
                "images/a/1.png": {"source": "p", "original": "x"},
                "images/b/1.png": {"source": "unknown", "todo": "replace it"},
                "images/b/c/2.png": {"source": "unknown", "todo": "replace it"},
                "sounds/s.wav": {"source": "unknown"},
            }
        )
    )
    assert "### Pending replacement" in text
    assert "The other 3 have no confirmed source" in text
    assert "- `assets/images/b/` (2 files): replace it" in text
    assert "- `assets/sounds/s.wav` (1 file): origin not confirmed" in text
    # The one known file is the only one in the pack table.
    assert "| things | 1 |" in text


def test_no_pending_section_when_every_source_is_known():
    text = gen_credits.render(
        _fake({"images/a/1.png": {"source": "p", "original": "x"}})
    )
    assert "Pending replacement" not in text
    assert "- Pack ([CC BY 3.0]" in text and "Au, with a link" in text


def test_every_pack_with_modified_files_says_what_changed(sources):
    modified = {e["source"] for e in sources["files"].values() if "modified" in e}
    for slug in modified:
        assert sources["packs"][slug].get("changes"), slug


def test_pending_lists_known_sources_with_a_todo_as_credited():
    text = gen_credits.render(
        _fake(
            {
                "sounds/m.wav": {"source": "p", "original": "x", "todo": "swap it"},
                "images/b/1.png": {"source": "unknown", "todo": "replace it"},
            }
        )
    )
    assert "- `assets/sounds/m.wav` (1 file, credited above): swap it" in text
    assert "- `assets/images/b/` (1 file): replace it" in text
    assert "The other 1 have no confirmed source" in text


def test_changes_are_rendered_per_pack():
    data = _fake({"images/a/1.png": {"source": "p", "original": "x", "modified": "m"}})
    data["packs"]["p"]["changes"] = "frames cut from the sheet"
    text = gen_credits.render(data)
    assert "### Changes to the original files" in text
    assert "- Pack: frames cut from the sheet" in text


def test_updated_credits_names_the_file_when_markers_are_misplaced():
    for text in ("no markers", f"{gen_credits.END}\n{gen_credits.BEGIN}"):
        with pytest.raises(ValueError, match="CREDITS.md"):
            gen_credits.updated_credits(text, "x")


def test_own_files_are_credited_by_how_they_were_made():
    text = gen_credits.render(
        _fake(
            {
                "images/a/1.png": {"source": "own", "generated_with": "SomeTool"},
                "images/a/2.png": {"source": "own", "generated_with": "SomeTool"},
                "images/b/3.png": {"source": "own"},
            }
        )
    )
    assert (
        "AI-generated by its developer with SomeTool and post-processed: "
        "1.png, 2.png (in assets/images/a)." in text
    )
    assert "Made for this game by its developer: 3.png (in assets/images/b)." in text
