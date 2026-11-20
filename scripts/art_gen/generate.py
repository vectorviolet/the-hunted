"""Generate the raw candidates with OpenAI Codex image generation (``codex exec``).

    uv run python scripts/art_gen/generate.py [job ...]      # default: every job in prompts.JOBS

Each job runs one ``codex exec`` with the three style references attached and copies the
generated picture to ``scripts/art_gen/work/raw/<job>.png`` (skipped when it already exists).
``work/`` is gitignored: the raw pictures are not committed (about 1.3 MB each), only the final
assets, the prompts and these scripts.
"""

from __future__ import annotations

import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from prompts import JOBS

HERE = Path(__file__).resolve().parent
RAW = HERE / "work" / "raw"
REFS = [
    HERE.parent / "sheets" / "vampire_sheet.png",
    HERE.parent / "sheets" / "peasant_sheet.png",
    HERE.parent / "icons" / "cand_a.png",  # icon A (PR #17)
]
PARALLEL = 4


def run_job(name: str) -> str:
    out = RAW / f"{name}.png"
    if out.exists():
        return f"{name}: exists"
    prompt = (
        "Use your image generation tool to make ONE image from this brief, using the attached "
        "images only as style references (do not copy their content):\n\n"
        f"{JOBS[name][1]}\n\n"
        f"When done, copy the generated file into the current directory as {name}.png and "
        "print its pixel size."
    )
    cmd = [
        "codex",
        "exec",
        "--skip-git-repo-check",
        "-s",
        "workspace-write",
        "-C",
        str(RAW),
    ]
    for ref in REFS:
        cmd += ["-i", str(ref)]
    cmd.append("-")
    proc = subprocess.run(
        cmd, input=prompt, text=True, capture_output=True, encoding="utf-8"
    )
    ok = out.exists()
    return f"{name}: {'ok' if ok else 'FAILED'}" + (
        "" if ok else "\n" + proc.stdout[-800:]
    )


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    names = sys.argv[1:] or list(JOBS)
    with ThreadPoolExecutor(PARALLEL) as pool:
        for line in pool.map(run_job, names):
            print(line, flush=True)


if __name__ == "__main__":
    main()
