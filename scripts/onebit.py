"""A one-bit desktop: the record in a window, the live run in front, and ~/skills dragged to the Trash."""
import datetime as dt
import sys

import cats
from pathlib import Path

from common import fmt_date, last_year, load_days, streaks, themed, tokens

PX = 2.5                       # one screen pixel in viewBox units: a 480 x 342 screen
SW, SH = 480, 342
THEMES = {
    "dark": {"ink": "#f2efe8", "paper": "#0a0a0a", "gray": "#5a606c", "eye": "#f2efe8", "chest": "#fbf3e6", "nose": "#f0a3a6", "amber": "#f2c53d", "green": "#c4cf5a", "desk_a": "#123f45", "desk_b": "#1d5a61", "bar": "#5cc0c6", "now": "#ec8a3c", "orange": "#ec8a3c", "stripe": "#b5601e"},
    "light": {"ink": "#0a0a0a", "paper": "#ffffff", "gray": "#4f5562", "eye": "#ffffff", "chest": "#fdf6ea", "nose": "#e8939a", "amber": "#f0c030", "green": "#b8c64e", "desk_a": "#3c8c93", "desk_b": "#64b3b7", "bar": "#2c7a82", "now": "#e5822f", "orange": "#e8873a", "stripe": "#ad5a1a"},
}

FONT = {
    "A": ".###.|#...#|#...#|#####|#...#|#...#|#...#", "B": "####.|#...#|#...#|####.|#...#|#...#|####.",
    "C": ".###.|#...#|#....|#....|#....|#...#|.###.", "D": "###..|#..#.|#...#|#...#|#...#|#..#.|###..",
    "E": "#####|#....|#....|####.|#....|#....|#####", "F": "#####|#....|#....|####.|#....|#....|#....",
    "G": ".###.|#...#|#....|#.###|#...#|#...#|.####", "H": "#...#|#...#|#...#|#####|#...#|#...#|#...#",
    "I": "###|.#.|.#.|.#.|.#.|.#.|###", "J": "..###|...#.|...#.|...#.|...#.|#..#.|.##..",
    "K": "#...#|#..#.|#.#..|##...|#.#..|#..#.|#...#", "L": "#....|#....|#....|#....|#....|#....|#####",
    "M": "#...#|##.##|#.#.#|#.#.#|#...#|#...#|#...#", "N": "#...#|#...#|##..#|#.#.#|#..##|#...#|#...#",
    "O": ".###.|#...#|#...#|#...#|#...#|#...#|.###.", "P": "####.|#...#|#...#|####.|#....|#....|#....",
    "Q": ".###.|#...#|#...#|#...#|#.#.#|#..#.|.##.#", "R": "####.|#...#|#...#|####.|#.#..|#..#.|#...#",
    "S": ".####|#....|#....|.###.|....#|....#|####.", "T": "#####|..#..|..#..|..#..|..#..|..#..|..#..",
    "U": "#...#|#...#|#...#|#...#|#...#|#...#|.###.", "V": "#...#|#...#|#...#|#...#|#...#|.#.#.|..#..",
    "W": "#...#|#...#|#...#|#.#.#|#.#.#|#.#.#|.#.#.", "X": "#...#|#...#|.#.#.|..#..|.#.#.|#...#|#...#",
    "Y": "#...#|#...#|.#.#.|..#..|..#..|..#..|..#..", "Z": "#####|....#|...#.|..#..|.#...|#....|#####",
    "0": ".###.|#...#|#..##|#.#.#|##..#|#...#|.###.", "1": ".#.|##.|.#.|.#.|.#.|.#.|###",
    "2": ".###.|#...#|....#|...#.|..#..|.#...|#####", "3": "####.|....#|....#|.###.|....#|....#|####.",
    "4": "...#.|..##.|.#.#.|#..#.|#####|...#.|...#.", "5": "#####|#....|####.|....#|....#|#...#|.###.",
    "6": "..##.|.#...|#....|####.|#...#|#...#|.###.", "7": "#####|....#|...#.|..#..|.#...|.#...|.#...",
    "8": ".###.|#...#|#...#|.###.|#...#|#...#|.###.", "9": ".###.|#...#|#...#|.####|....#|...#.|.##..",
    ",": "..|..|..|..|.#|.#|#.", ".": ".|.|.|.|.|.|#", ":": ".|.|#|.|.|#|.", "-": "....|....|....|####|....|....|....",
    "/": "....#|....#|...#.|..#..|.#...|#....|#....", "~": ".....|.....|.#..#|#.##.|.....|.....|.....",
    "'": "#|#|.|.|.|.|.", "(": "..#|.#.|#..|#..|#..|.#.|..#", ")": "#..|.#.|..#|..#|..#|.#.|#..",
    " ": "...|...|...|...|...|...|...", "#": ".#.#.|.#.#.|#####|.#.#.|#####|.#.#.|.#.#.",
}
FOLDER = ["..#####.........", ".#.....#........", "################", "#..............#",
          "#..............#", "#..............#", "#..............#", "#..............#",
          "#..............#", "#..............#", "#..............#", "################"]
TRASH = [".....#####.....", "....#.....#....", "###############", "#.............#",
         "###############", ".#...........#.", ".#.#..#..#.#..#", ".#.#..#..#.#..#",
         ".#.#..#..#.#..#", ".#.#..#..#.#..#", ".#.#..#..#.#..#", ".#.#..#..#.#..#",
         ".#.#..#..#.#..#", ".#.#..#..#.#..#", ".#.#..#..#.#..#", ".#...........#.",
         "..###########.."]
TRASH_FULL = ["..........#####", ".........#....#", "......#########", "...#####.....#.",
              "..#....#######.", "..###########..", "###############", "#.............#",
              "###############", ".#...........#.", ".#.#..#..#.#..#", ".#.#..#..#.#..#",
              ".#.#..#..#.#..#", ".#.#..#..#.#..#", ".#.#..#..#.#..#", ".#...........#.",
              "..###########.."]
# A desktop cat, 16px sprites drawn at 2x: '#' ink, 'o' paper, '.' clear. Feet sit on the bottom row.
CAT_SIT = ["..#..........#..", "..##........##..", "..#o#......#o#..", "..#oo######oo#..",
           "..#oooooooooo#..", ".#oo#oooooo#oo#.", ".#oo#oooooo#oo#.", ".#ooooo##ooooo#.",
           "..#oooooooooo#..", "...##oooooo##...", "...#oooooooo#.##", "..#oooooooooo#.#",
           "..#oooooooooo##.", "..#oo#oooo#oo#..", "..#oo#oooo#oo#..", "..############.."]
CAT_WALK_A = ["............#.#.", "............###.", "#..........#ooo#", "#..........#o#o#",
              ".#.#########ooo#", ".##ooooooooooo#.", "..#oooooooooo#..", "..#oooooooooo#..",
              "..#oo######oo#..", "..#o#......#o#..", ".#o#........#o#.", ".##..........##."]
CAT_WALK_B = CAT_WALK_A[:9] + ["...#o#....#o#...", "...#o#....#o#...", "...##......##..."]
CAT_SLEEP_A = [".#.#............", ".###..#######...", "#ooo##ooooooo##.", "#oooooooooooooo#",
               "#o##ooooooooooo#", "#oooooooooooooo#", ".#oo#######ooo#.", "..##.......###.."]
CAT_SLEEP_B = [".#.#...#####....", ".###..#ooooo#...", "#ooo##ooooooo##.", "#oooooooooooooo#",
               "#o##ooooooooooo#", "#oooooooooooooo#", ".#oo#######ooo#.", "..##.......###.."]
DISK = [".######################.", "#......................#", "#......................#",
        "#......................#", "#......................#", "#......................#",
        "#......................#", "#.##...................#", "#......................#",
        ".######################."]


def runs(rows, x, y, s=1):
    """Path data for a bitmap: horizontal runs of set pixels, each pixel s screen pixels."""
    d = []
    for j, row in enumerate(rows):
        i = 0
        while i < len(row):
            if row[i] == "#":
                k = i
                while k < len(row) and row[k] == "#":
                    k += 1
                d.append(f"M{(x + i * s) * PX:g},{(y + j * s) * PX:g}h{(k - i) * s * PX:g}v{s * PX:g}h-{(k - i) * s * PX:g}z")
                i = k
            else:
                i += 1
    return "".join(d)


def sprite(rows, t, s=3, anchor="feet"):
    """Opaque pixel sprite drawn at the origin: feet on y=0, or top-left at 0,0 with anchor="top"."""
    top = -len(rows) * s if anchor == "feet" else 0
    fill = [r.replace("o", "#") for r in rows]
    ink = [r.replace("o", ".") for r in rows]
    return (f'<path d="{runs(fill, 0, top, s)}" fill="{t["paper"]}"/>'
            f'<path d="{runs(ink, 0, top, s)}" fill="{t["ink"]}"/>')


def text_w(text, s=1):
    return sum((len(FONT[c].split("|")[0]) + 1) * s for c in text.upper()) - s


def text(t, x, y, s=1, anchor="start"):
    t = t.upper()
    x -= {"start": 0, "middle": text_w(t, s) // 2, "end": text_w(t, s)}[anchor]
    d = []
    for c in t:
        rows = FONT[c].split("|")
        d.append(runs(rows, x, y, s))
        x += (len(rows[0]) + 1) * s
    return "".join(d)


def rect(x, y, w, h):
    return f"M{x * PX:g},{y * PX:g}h{w * PX:g}v{h * PX:g}h-{w * PX:g}z"


def frame(x, y, w, h):
    """One-pixel outline as a path ring."""
    return rect(x, y, w, h) + rect(x + 1, y + 1, w - 2, h - 2)


def window(x, y, w, h, title, active):
    t = tokens(THEMES)
    out = [f'<path d="{rect(x + 1, y + 1, w, h)}" fill="{t["ink"]}"/>',            # 1px drop shadow
           f'<path d="{rect(x, y, w, h)}" fill="{t["paper"]}"/>',
           f'<path d="{frame(x, y, w, h)}" fill="{t["ink"]}" fill-rule="evenodd"/>',
           f'<path d="{rect(x, y + 12, w, 1)}" fill="{t["ink"]}"/>']
    if active:
        stripes = "".join(rect(x + 2, y + 3 + k * 2, w - 4, 1) for k in range(4))
        out.append(f'<path d="{stripes}" fill="{t["ink"]}"/>')
        tw = text_w(title) + 10
        out.append(f'<path d="{rect(x + w // 2 - tw // 2, y + 2, tw, 9)}" fill="{t["paper"]}"/>')
        out.append(f'<path d="{rect(x + 8, y + 3, 9, 7)}" fill="{t["paper"]}"/>'
                   f'<path d="{frame(x + 9, y + 3, 7, 7)}" fill="{t["ink"]}" fill-rule="evenodd"/>')
    out.append(f'<path d="{text(title, x + w // 2, y + 3, 1, "middle")}" fill="{t["ink"]}"/>')
    return "".join(out)


def build(out, act="nap", palette="bit"):
    t = tokens(THEMES)
    days = load_days()
    s = streaks(days)
    rec, cur = s["longest"], s["current"]
    ly = last_year()
    today = dt.date.fromisoformat(s["today"])
    body, defs = [], []

    # Desktop: 50% dither, menu bar, rounded screen corners
    defs.append(f'<pattern id="dither" width="{2 * PX}" height="{2 * PX}" patternUnits="userSpaceOnUse">'
                f'<path d="{rect(0, 0, 1, 1)}{rect(1, 1, 1, 1)}" fill="{t["ink"]}"/></pattern>'
                f'<pattern id="d25" width="{2 * PX}" height="{2 * PX}" patternUnits="userSpaceOnUse">'
                f'<path d="{rect(0, 0, 1, 1)}" fill="{t["ink"]}"/></pattern>')
    body.append(f'<rect width="{SW * PX}" height="{SH * PX}" fill="{t["paper"]}"/>'
                f'<rect y="{13 * PX}" width="{SW * PX}" height="{(SH - 13) * PX}" fill="url(#dither)"/>')
    if palette == "colour":
        defs.append(f'<pattern id="desk" width="{2 * PX}" height="{2 * PX}" patternUnits="userSpaceOnUse">'
                    f'<path d="{rect(0, 0, 1, 1)}{rect(1, 1, 1, 1)}" fill="{t["desk_a"]}"/></pattern>')
        body.append(f'<rect y="{13 * PX}" width="{SW * PX}" height="{(SH - 13) * PX}" fill="{t["desk_b"]}"/>'
                    f'<rect y="{13 * PX}" width="{SW * PX}" height="{(SH - 13) * PX}" fill="url(#desk)"/>')
    body.append(f'<path d="{rect(0, 12, SW, 1)}" fill="{t["ink"]}"/>')
    menu = [("ARAF", 20), ("FILE", 52), ("EDIT", 80), ("VIEW", 108), ("SPECIAL", 136)]
    paw = ["..#.#..", ".#...#.", "...#...", "..###..", ".#####.", ".#####."]
    body.append(f'<path d="{runs(paw, 9, 3)}" fill="{t["now"] if palette == "colour" else t["ink"]}"/>')
    body.append(f'<path d="{text(today.strftime("%a %d %b").upper(), SW - 12, 3, 1, "end")}" fill="{t["ink"]}"/>')
    body.append(f'<path d="{"".join(text(m, x, 3) for m, x in menu)}" fill="{t["ink"]}"/>')

    # Desktop icons
    def icon(bitmap, x, y, label, cls=""):
        w = len(bitmap[0])
        lw = text_w(label) + 4
        return (f'<g class="{cls}"><path d="{runs([r.replace(".", "#") for r in bitmap], x, y)}" fill="{t["paper"]}"/>'
                f'<path d="{runs(bitmap, x, y)}" fill="{t["ink"]}"/>'
                f'<path d="{rect(x + w // 2 - lw // 2, y + len(bitmap) + 3, lw, 9)}" fill="{t["paper"]}"/>'
                f'<path d="{text(label, x + w // 2, y + len(bitmap) + 4, 1, "middle")}" fill="{t["ink"]}"/></g>')

    body.append(icon(DISK, 434, 22, "ARAF HD"))
    body.append(icon(TRASH, 439, 294, "TRASH"))

    # Window 1: the record (inactive, behind)
    wx, wy, ww, wh = 14, 22, 318, 148
    body.append(window(wx, wy, ww, wh, "THE RECORD", False))
    body.append(f'<path d="{text(format(rec["length"], ","), wx + 14, wy + 24, 6)}" fill="{t["ink"]}"/>')
    body.append(f'<path d="{text("DAY STREAK", wx + 15, wy + 76, 2)}" fill="{t["ink"]}"/>')
    body.append(f'<path d="{text(fmt_date(rec["start"]) + " - " + fmt_date(rec["end"]), wx + 15, wy + 98)}" fill="{t["ink"]}"/>')
    # The record as a contribution grid: one 2px cell per day, and every one of them is set
    start = dt.date.fromisoformat(rec["start"])
    end = dt.date.fromisoformat(rec["end"])
    gx, gy = wx + 15, wy + 114
    origin = start - dt.timedelta(days=start.weekday())
    cells, d = [], start
    while d <= end:
        if days.get(d.isoformat(), 0):
            cells.append(rect(gx + (d - origin).days // 7 * 2, gy + d.weekday() * 2, 2, 2))
        d += dt.timedelta(days=1)
    body.append(f'<path d="{"".join(cells)}" fill="{t["bar"] if palette == "colour" else t["ink"]}"/>')
    weeks = (end - origin).days // 7 + 1
    ticks = []
    for year in range(start.year + 1, end.year + 1):
        tx = gx + (dt.date(year, 1, 1) - origin).days // 7 * 2
        ticks.append(rect(tx, gy + 15, 1, 3))
        body.append(f'<path d="{text(str(year), tx + 3, gy + 17)}" fill="{t["ink"]}"/>')
    body.append(f'<path d="{"".join(ticks)}" fill="{t["ink"]}"/>')

    # Window 2: the last year (active, in front), monthly totals as one-bit bars
    rx, ry, rw, rh = 196, 140, 236, 122
    body.append('<g class="fx lastwin">')
    body.append(window(rx, ry, rw, rh, "LAST YEAR", True))
    body.append(f'<path d="{text(format(ly["total"], ","), rx + 14, ry + 22, 4)}" fill="{t["ink"]}"/>')
    body.append(f'<path d="{text("CONTRIBUTIONS IN THE LAST YEAR", rx + 15, ry + 56)}" fill="{t["ink"]}"/>')
    ys = dt.date.fromisoformat(ly["start"])
    months, (y, m) = [], (ys.year, ys.month)
    while (y, m) <= (today.year, today.month):
        months.append(sum(n for d, n in days.items() if d.startswith(f"{y}-{m:02d}-") and d >= ly["start"]))
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    bw, bh, bx0, by0 = 12, 32, rx + 15, ry + 104
    peak = max(months)
    bars = []
    for i, total in enumerate(months):
        h = max(1, round(bh * total / peak))
        bars.append(rect(bx0 + i * (bw + 3), by0 - h, bw, h))
    bar_fill = t["bar"] if palette == "colour" else "url(#dither)"
    body.append(f'<path d="{"".join(bars[:-1])}" fill="{bar_fill}"/>'
                f'<path d="{bars[-1]}" fill="{t["now"] if palette == "colour" else bar_fill}"/>'
                f'<path d="{rect(bx0, by0, len(months) * (bw + 3) - 3, 1)}" fill="{t["ink"]}"/>')
    lh = max(1, round(bh * months[-1] / peak))
    body.append(f'<rect class="ants" x="{(bx0 + (len(months) - 1) * (bw + 3) - 1) * PX}" y="{(by0 - lh - 1) * PX}" '
                f'width="{(bw + 2) * PX}" height="{(lh + 1) * PX}" fill="none" stroke="{t["ink"]}" stroke-width="{PX}" '
                f'stroke-dasharray="{PX} {PX}"/>')
    body.append(f'<path d="{text("CURRENT STREAK: " + str(cur["length"]) + " DAYS", rx + 15, ry + 110)}" fill="{t["ink"]}"/>')
    body.append('</g>')

    # The desk cat
    bars_xy = [(bx0 + i * (bw + 3), by0 - max(1, round(bh * total / peak))) for i, total in enumerate(months)]
    kit = {"t": t, "PX": PX, "sprite": sprite, "text": text, "rect": rect, "window": window}
    layout = {"rx": rx, "ry": ry, "rw": rw, "rh": rh, "bars": bars_xy}
    cat_svg, cat_css, T, cat_alt = cats.ACTS[act](layout, kit, palette)
    body.append(cat_svg)

    corners = "".join(
        f'<path d="M{cx},{cy} h{sx * 6 * PX} a{6 * PX},{6 * PX} 0 0 {0 if sx * sy > 0 else 1} {-sx * 6 * PX},{sy * 6 * PX} z" fill="#000"/>'
        for cx, cy, sx, sy in ((0, 0, 1, 1), (SW * PX, 0, -1, 1), (0, SH * PX, 1, -1), (SW * PX, SH * PX, -1, -1)))

    W, H = SW * PX, SH * PX
    alt = (f"One-bit desktop: a {rec['length']:,}-day streak, {fmt_date(rec['start'], False)} to "
           f"{fmt_date(rec['end'], False)}; {ly['total']:,} contributions in the last year; current streak "
           f"{cur['length']} days. Then {cat_alt}.")
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W:g} {H:g}" width="{W:g}" height="{H:g}" role="img" shape-rendering="crispEdges">
<title>{alt}</title>
<style>
.ants{{animation:ants .5s steps(2) infinite}}
@keyframes ants{{to{{stroke-dashoffset:{2 * PX}}}}}
{chr(10).join(cats.common_css(T, kit) + cat_css)}
{cats.REDUCED}
</style>
<defs>{"".join(defs)}</defs>
{"".join(body)}
{corners}
</svg>"""
    css, svg = themed(svg, THEMES)
    svg = svg.replace("<style>", "<style>" + css, 1)
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(svg)


if __name__ == "__main__":
    for act in (sys.argv[2:] or cats.ACTS):
        build(Path(sys.argv[1]) / f"cat-{act}.svg", act)
        if act in ("brawl", "truce", "zoomies"):
            build(Path(sys.argv[1]) / f"cat-{act}-colour.svg", act, "colour")
    print("ok")
