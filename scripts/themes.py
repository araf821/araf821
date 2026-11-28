"""Seasonal looks for the contributions plate. The refresh picks one by date; THEME=<name> forces one."""
import datetime as dt
import os

DEFAULT = {
    "palette": {
        "ground": "#0a110d", "line": "#1c2b22", "ink": "#ece6d6", "muted": "#8b9a8f", "faint": "#56665a",
        "empty": "#121c16", "now": "#ff9d4a",
        "ramp": ["#21492e", "#2b6b40", "#3a9149", "#76c25f", "#c6ec86"],
    },
    "falling": (),     # weather layers drifting over the card
    "ledge": (),       # what lies along each year's top edge: snow, leaves, lights
    "settle": None,    # what lands on the napping gray cat: snow or a leaf
    "bulbs": (),       # light colours when the ledge has lights
    "scarf": None,     # one colour, or (base, stripe)
    "hat": None,
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
        "ledge": ("snow",),
        "settle": "snow",
        "scarf": "#c9433c",
    },
    "fall": {
        "palette": {
            "ground": "#0f1318", "line": "#232a33", "ink": "#efe8dc", "muted": "#9c9a94", "faint": "#61666d",
            "empty": "#161a1f", "now": "#a9d6ff",
            "ramp": ["#553d2d", "#74503a", "#996640", "#bd8749", "#dcb26e"],
        },
        "falling": ("leaves", "flurries"),
        "ledge": ("leaves",),
        "settle": "leaf",
        "scarf": "#3f6e57",
    },
    "holidays": {
        "palette": {
            "ground": "#120d10", "line": "#2b1d22", "ink": "#f7f1ea", "muted": "#ab9ea2", "faint": "#6d5f64",
            "empty": "#1d1418", "now": "#ffd36b",
            "ramp": ["#5a1d25", "#86232d", "#b82a35", "#e2535a", "#ffc9c9"],
        },
        "falling": ("snow", "sparkles"),
        "ledge": ("snow", "lights"),
        "bulbs": ("#ff4a4a", "#fff4e0", "#ffd36b", "#fff4e0"),
        "settle": "snow",
        "scarf": ("#d8333a", "#f6f1ea"),
        "hat": "#d8333a",
    },
}

# (first day, last day, theme) as (month, day); windows may wrap past New Year. First match wins,
# so single holidays go above the seasons they sit in.
SEASONS = [
    ((12, 20), (1, 3), "holidays"),
    ((10, 20), (12, 9), "fall"),
    ((12, 10), (2, 28), "winter"),
]


def _within(today, first, last):
    key = (today.month, today.day)
    return first <= key <= last if first <= last else key >= first or key <= last


def pick(today: dt.date):
    name = os.environ.get("THEME") or next((t for a, b, t in SEASONS if _within(today, a, b)), "default")
    return name, {**DEFAULT, **THEMES[name]}
