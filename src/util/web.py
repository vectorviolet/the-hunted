"""The browser side of the web build (pygbag, `sys.platform == "emscripten"`)."""

import sys


def is_web() -> bool:
    """True in the browser build. Read at call time (not import time) so a test
    can pretend to be the browser by patching `sys.platform`."""
    return sys.platform == "emscripten"
