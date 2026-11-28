"""Seasonal looks for the contributions plate. The refresh picks one by date; THEME=<name> forces one."""
import datetime as dt
import os

DEFAULT = {
    "palette": {
        "ground": "#0a110d", "line": "#1c2b22", "ink": "#ece6d6", "muted": "#8b9a8f", "faint": "#56665a",
        "empty": "#121c16", "now": "#ff9d4a",
        "ramp": ["#21492e", "#2b6b40", "#3a9149", "#76c25f", "#c6ec86"],
    },
    "falling": (),
    "scarf": None,
}

THEMES = {
    "default": DEFAULT,
    "winter": {
        "palette": {
            "ground": "#0b1320", "line": "#1d2b3f", "ink": "#eef3f8", "muted": "#94a6ba", "faint": "#5a6d83",
            "empty": "#131e2d", "now": "#ff9d4a",
            "ramp": ["#22436a", "#2c5f8e", "#3d7fb8", "#80b6e3", "#d9edff"],
        },
        "falling": ("snow",),
        "scarf": "#c9433c",
    },
    "fall": {
        "palette": {
            "ground": "#0f1318", "line": "#232a33", "ink": "#efe8dc", "muted": "#9c9a94", "faint": "#61666d",
            "empty": "#161a1f", "now": "#a9d6ff",
            "ramp": ["#553d2d", "#74503a", "#996640", "#bd8749", "#dcb26e"],
        },
        "falling": ("leaves", "flurries"),
        "scarf": "#3f6e57",
    },
}

# (first day, last day, theme) as (month, day); windows may wrap past New Year. First match wins,
# so single holidays go above the seasons they sit in.
SEASONS = [
    ((10, 20), (12, 15), "fall"),
    ((12, 16), (2, 28), "winter"),
]


def _within(today, first, last):
    key = (today.month, today.day)
    return first <= key <= last if first <= last else key >= first or key <= last


def pick(today: dt.date):
    name = os.environ.get("THEME") or next((t for a, b, t in SEASONS if _within(today, a, b)), "default")
    return name, THEMES[name]
