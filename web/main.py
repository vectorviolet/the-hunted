# /// script
# dependencies = [
#   "pygame-ce",
#   "pyyaml",
# ]
# ///
"""Entry point of the web build (pygbag), staged as `main.py` at the root of
the bundle next to `src/` and `assets/`. The desktop entry point is
`__main__.py`; this one runs the game's loop through `run_async()` so the
browser gets control back after every frame."""

import asyncio
import os
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT / "src" / "pygamine"))
os.chdir(_ROOT)


async def main() -> None:
    try:
        from game import Game

        await Game().run_async()
    except Exception:
        import traceback

        error = traceback.format_exc()
        print(error)
        if sys.platform == "emscripten":
            import platform

            panel = platform.window.document.createElement("pre")
            panel.textContent = "The Hunted could not start.\n\n" + error
            panel.style.cssText = (
                "position:fixed;inset:0;z-index:9999;overflow:auto;"
                "background:#140e14;color:#d9d7dc;padding:24px;white-space:pre-wrap;"
                "font:16px monospace"
            )
            platform.window.document.body.appendChild(panel)
        else:
            raise


asyncio.run(main())
