"""Shared data + type helpers for the README plates."""
import datetime as dt
import json
import os
import re
import subprocess
from functools import lru_cache
from pathlib import Path
from zoneinfo import ZoneInfo

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont

LAB = Path(__file__).resolve().parent.parent
FONTS = LAB / "fonts"
USER = "araf821"

QUERY = """query($login:String!,$from:DateTime!,$to:DateTime!){user(login:$login){
contributionsCollection(from:$from,to:$to){contributionCalendar{weeks{contributionDays{date contributionCount}}}}}}"""


def fetch_days(first_year=2020, today=None):
    """Daily contribution counts {iso_date: count} from the GraphQL calendar, via gh."""
    today = today or dt.date.today()
    days = {}
    for year in range(first_year, today.year + 1):
        out = subprocess.run(
            ["gh", "api", "graphql", "-f", f"query={QUERY}", "-f", f"login={USER}",
             "-f", f"from={year}-01-01T00:00:00Z", "-f", f"to={year}-12-31T23:59:59Z"],
            capture_output=True, text=True, check=True).stdout
        cal = json.loads(out)["data"]["user"]["contributionsCollection"]["contributionCalendar"]
        for week in cal["weeks"]:
            for d in week["contributionDays"]:
                if d["date"] <= today.isoformat():
                    days[d["date"]] = d["contributionCount"]
    return days


def load_days():
    cache = LAB / ".cache" / "days.json"
    if os.environ.get("REFRESH") or not cache.exists():
        cache.parent.mkdir(exist_ok=True)
        cache.write_text(json.dumps(fetch_days()))
    today = dt.date.today().isoformat()
    return {d: n for d, n in json.loads(cache.read_text()).items() if d <= today}


def last_year():
    """The profile's own figure: total and window of contributionsCollection with no range."""
    cache = LAB / ".cache" / "last_year.json"
    if os.environ.get("REFRESH") or not cache.exists():
        q = f'query{{user(login:"{USER}"){{contributionsCollection{{startedAt contributionCalendar{{totalContributions}}}}}}}}'
        out = json.loads(subprocess.run(["gh", "api", "graphql", "-f", f"query={q}"],
                                        capture_output=True, text=True, check=True).stdout)
        c = out["data"]["user"]["contributionsCollection"]
        utc = dt.datetime.fromisoformat(c["startedAt"].replace("Z", "+00:00"))
        local_start = utc.astimezone(ZoneInfo("America/Toronto")).date()
        cache.write_text(json.dumps({"total": c["contributionCalendar"]["totalContributions"],
                                     "start": local_start.isoformat()}))
    return json.loads(cache.read_text())


def streaks(days):
    """Longest and current runs of consecutive days with at least one contribution."""
    dates = sorted(days)
    best, run, start = (0, None, None), 0, None
    for d in dates:
        if days[d] > 0:
            start = d if run == 0 else start
            run += 1
            if run > best[0]:
                best = (run, start, d)
        else:
            run = 0
    today = dt.date.fromisoformat(dates[-1])
    cursor = today if days[dates[-1]] > 0 else today - dt.timedelta(days=1)
    cur = 0
    while days.get(cursor.isoformat(), 0) > 0:
        cur += 1
        cursor -= dt.timedelta(days=1)
    cur_start = cursor + dt.timedelta(days=1)
    return {
        "longest": {"length": best[0], "start": best[1], "end": best[2]},
        "current": {"length": cur, "start": cur_start.isoformat(), "end": today.isoformat()},
        "total": sum(days.values()),
        "today": today.isoformat(),
    }


class Face:
    """A font instance that sets text as SVG path data (no font loading inside <img>)."""

    def __init__(self, file, **axes):
        font = TTFont(FONTS / file)
        if axes and "fvar" in font:
            font = instantiateVariableFont(font, axes)
        self.glyphs = font.getGlyphSet()
        self.cmap = font.getBestCmap()
        self.upm = font["head"].unitsPerEm
        self.hmtx = font["hmtx"]
        self.cap = getattr(font["OS/2"], "sCapHeight", 0.7 * self.upm) / self.upm

    def _names(self, text):
        return [self.cmap.get(ord(c), ".notdef") for c in text]

    def width(self, text, size, track=0.0):
        adv = sum(self.hmtx[n][0] for n in self._names(text)) * size / self.upm
        return adv + track * size * max(len(text) - 1, 0)

    def path(self, text, x, y, size, track=0.0, anchor="start"):
        w = self.width(text, size, track)
        x -= {"start": 0, "middle": w / 2, "end": w}[anchor]
        s = size / self.upm
        pen = SVGPathPen(self.glyphs)
        for name in self._names(text):
            self.glyphs[name].draw(TransformPen(pen, (s, 0, 0, -s, x, y)))
            x += self.hmtx[name][0] * s + track * size
        return re.sub(r"-?\d+\.\d+", lambda m: f"{float(m.group()):.1f}".rstrip("0").rstrip("."), pen.getCommands())


@lru_cache(maxsize=None)
def face(file, **axes):
    return Face(file, **axes)


def fmt_date(iso, upper=True):
    d = dt.date.fromisoformat(iso)
    s = d.strftime("%d %b %Y")
    return s.upper() if upper else s


TOKEN = re.compile(r'\s(fill|stroke)="@([\w-]+)"')


def themed(svg_body, themes, default="dark"):
    """Swap fill/stroke="@token" for CSS variables; the SVG follows the viewer's colour scheme."""
    def tag(m):
        attrs = TOKEN.findall(m.group(0))
        if not attrs:
            return m.group(0)
        clean = TOKEN.sub("", m.group(0))
        style = ";".join(f"{a}:var(--{n})" for a, n in attrs)
        return clean.replace("<", "<", 1).rstrip("/>").rstrip() + f' style="{style}"' + ("/>" if m.group(0).endswith("/>") else ">")

    body = re.sub(r"<[a-zA-Z][^<>]*>", tag, svg_body)
    other = next(k for k in themes if k != default)
    var = lambda t: ";".join(f"--{k}:{v}" for k, v in t.items())
    css = f":root{{{var(themes[default])}}}@media (prefers-color-scheme:{other}){{:root{{{var(themes[other])}}}}}"
    return css, body


def tokens(themes):
    return {k: f"@{k}" for k in next(iter(themes.values()))}
