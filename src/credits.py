"""The credits page's text: the generated `credits_data.SECTIONS`.

scripts/gen_credits.py builds it from assets/SOURCES.yaml (the data CREDITS.md's asset table
comes from too), so the two can't disagree about who made what, and writes it to
credits_data.py. The game never reads the YAML, so it needs no YAML library (the browser build
has none).
"""

from credits_data import SECTIONS

CreditSection = tuple[str, list[str]]


def load_credit_sections() -> list[CreditSection]:
    """The credits the game shows, as (heading, lines) pairs."""
    return [(heading, list(lines)) for heading, lines in SECTIONS]
