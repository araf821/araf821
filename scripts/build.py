"""Regenerate the README desktop from live GitHub data: python scripts/build.py"""
import os
from pathlib import Path

os.environ.setdefault("REFRESH", "1")
import onebit  # noqa: E402

onebit.build(Path(__file__).resolve().parent.parent / "assets" / "desk.svg", "brawl", "colour", "forest", ("odometer", "grow", "live"))
print("assets/desk.svg")
