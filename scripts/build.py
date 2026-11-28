"""Regenerate the README plate from live GitHub data: python scripts/build.py"""
import os
from pathlib import Path

os.environ.setdefault("REFRESH", "1")
import contributions  # noqa: E402

contributions.build(Path(__file__).resolve().parent.parent / "assets" / "contributions.svg")
print("assets/contributions.svg")
