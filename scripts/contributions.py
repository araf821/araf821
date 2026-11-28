"""The contributions plate: every year since 2023 as a paw grid, with the cats chasing through it."""
import datetime as dt
import math
import random
from pathlib import Path

import themes
import vcats
from common import face, last_year, load_days, streaks

W = 1200
RECORD = 1007
FIRST_YEAR = 2023
NUM = face("Geist[wght].ttf", wght=620)
NUM_L = face("Geist[wght].ttf", wght=480)
PIX = face("DepartureMono-Regular.otf")
PAW = ["..#.#..", "#.....#", "...#...", ".#####.", ".#####.", "..###.."]


def label(text, x, y, size, fill, anchor="start", track=0.04):
    return f'<path d="{PIX.path(text.upper(), x, y, size, track, anchor)}" fill="{fill}"/>'


def paw(x, y, s):
    return "".join(f"M{x + i * s:g},{y + j * s:g}h{s}v{s}h-{s}z"
                   for j, row in enumerate(PAW) for i, ch in enumerate(row) if ch == "#")


def cell(x, y, size, fill, paw_fill=None, r=4):
    out = f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{r}" fill="{fill}"/>'
    if paw_fill:
        s = 2 if size >= 16 else 1.6
        out += f'<path d="{paw(x + (size - 7 * s) / 2, y + (size - 6 * s) / 2 + .5, s)}" fill="{paw_fill}"/>'
    return out


def header(C, total, current):
    out = [f'<path d="{NUM.path(format(total, ","), 56, 148, 112, -0.02)}" fill="{C["ink"]}"/>',
           label("contributions in the last year", 60, 194, 24, C["muted"])]
    x = W - 56
    for big, cap in reversed([(str(current), "current streak"), (format(RECORD, ","), "longest streak")]):
        uw = NUM_L.width(" days", 30)
        out.append(f'<path d="{NUM_L.path(" days", x, 148, 30, 0, "end")}" fill="{C["muted"]}"/>')
        out.append(f'<path d="{NUM.path(big, x - uw, 148, 56, -0.02, "end")}" fill="{C["ink"]}"/>')
        out.append(label(cap, x, 194, 20, C["muted"], "end"))
        x -= max(NUM.width(big, 56, -0.02) + uw, PIX.width(cap.upper(), 20, .04)) + 56
    return "".join(out)


def first_sunday(year):
    jan1 = dt.date(year, 1, 1)
    return jan1 - dt.timedelta((jan1.weekday() + 1) % 7)


def snowfall(h, n=64, sizes=(1.4, 1.8, 2.3, 2.9, 3.6)):
    """Flakes drifting down the whole card on loops that never line up; seeded so the file only changes with the data."""
    rnd = random.Random(1225)
    flakes, css = [], [".flake{animation:fall linear infinite}.sway{animation:sway ease-in-out infinite alternate}"
                       f"@keyframes fall{{from{{transform:translate(0,-12px)}}to{{transform:translate(0,{h + 24}px)}}}}"
                       "@keyframes sway{from{transform:translate(-7px,0)}to{transform:translate(7px,0)}}"]
    for i in range(n):
        r = rnd.choice(sizes)
        dur = 16 - r * 2.6 + rnd.uniform(-1.5, 1.5)
        flakes.append(f'<g class="flake" style="animation-duration:{dur:.1f}s;animation-delay:-{rnd.uniform(0, dur):.1f}s">'
                      f'<g class="sway" style="animation-duration:{rnd.uniform(2.2, 4.2):.1f}s;animation-delay:-{rnd.uniform(0, 4):.1f}s">'
                      f'<circle cx="{rnd.uniform(8, W - 8):.0f}" cy="0" r="{r}" fill="#fff" opacity="{min(.95, .4 + r * .15):.2f}"/></g></g>')
    return "".join(flakes), css


LEAF_COLOURS = ("#8c4a2b", "#a65a30", "#b9803f", "#6e4a33", "#9b6b3a")


def leaffall(h, n=20):
    """Leaves blown across the card left to right, tumbling as they fall; seeded like the snow."""
    rnd = random.Random(1031)
    leaves, css = [], [".blow{animation:blow linear infinite}.flutter{animation:flutter ease-in-out infinite alternate}"
                       ".tumble{animation:tumble linear infinite}"
                       f"@keyframes blow{{from{{transform:translate(-60px,-20px)}}to{{transform:translate(160px,{h + 30}px)}}}}"
                       "@keyframes flutter{from{transform:translate(-14px,0)}to{transform:translate(14px,0)}}"
                       "@keyframes tumble{to{transform:rotate(360deg)}}"]
    for i in range(n):
        dur = rnd.uniform(9, 15)
        spin = rnd.uniform(2.6, 5.5) * rnd.choice((1, -1))
        leaves.append(
            f'<g class="blow" style="animation-duration:{dur:.1f}s;animation-delay:-{rnd.uniform(0, dur):.1f}s">'
            f'<g class="flutter" style="animation-duration:{rnd.uniform(1.6, 3.2):.1f}s;animation-delay:-{rnd.uniform(0, 3):.1f}s">'
            f'<g transform="translate({rnd.uniform(-40, W - 80):.0f},0)">'
            f'<g class="tumble" style="animation-duration:{abs(spin):.1f}s;animation-direction:{"normal" if spin > 0 else "reverse"}">'
            f'{vcats.leaf(rnd.randrange(2), rnd.choice(LEAF_COLOURS), rnd.uniform(1.5, 2.3))}</g></g></g></g>')
    return "".join(leaves), css


def litter(x0, x1, y, seed, n=14):
    """A few fallen leaves lying along the top edge of a year's grid."""
    rnd = random.Random(seed)
    return "".join(
        f'<g transform="translate({rnd.uniform(x0, x1):.0f},{y + rnd.uniform(-1.5, 1):.1f}) rotate({rnd.uniform(60, 120) * rnd.choice((1, -1)):.0f})">'
        f'{vcats.leaf(rnd.randrange(2), rnd.choice(LEAF_COLOURS), rnd.uniform(1.1, 1.5))}</g>' for _ in range(n))


def lights(x0, x1, y, seed, colours):
    """A string of lights swagged along a year's top edge, each bulb twinkling on its own beat."""
    rnd = random.Random(seed)
    count = max(3, round((x1 - x0) / 100))
    swag, sag = (x1 - x0) / count, 9
    wire, bulbs = [f"M{x0:.1f},{y}"], []
    for i in range(count):
        a = x0 + i * swag
        wire.append(f"Q{a + swag / 2:.1f},{y + sag * 2} {a + swag:.1f},{y}")
        for t in (.2, .4, .6, .8):
            bx = a + swag * t
            by = y + sag * 2 * 2 * t * (1 - t)
            colour = colours[(i * 4 + int(t * 5)) % len(colours)]
            dur, dl = rnd.uniform(1.4, 3.2), rnd.uniform(0, 3)
            bulbs.append(f'<g class="bulb" style="animation-duration:{dur:.1f}s;animation-delay:-{dl:.1f}s">'
                         f'<circle cx="{bx:.1f}" cy="{by + 5:.1f}" r="9.5" fill="{colour}" opacity=".24"/>'
                         f'<ellipse cx="{bx:.1f}" cy="{by + 5.6:.1f}" rx="3.2" ry="4.4" fill="{colour}"/></g>'
                         f'<rect x="{bx - 1.6:.1f}" y="{by:.1f}" width="3.6" height="2.6" rx=".7" fill="#2b3346"/>')
    return f'<path d="{"".join(wire)}" fill="none" stroke="#2b3346" stroke-width="1.3"/>' + "".join(bulbs)


def sparkles(h, n=16):
    """Four-point glints scattered over the card, each fading in and out."""
    rnd = random.Random(2412)
    out, css = [], [".glint{transform-box:fill-box;transform-origin:50% 50%;animation:glint ease-in-out infinite}"
                    "@keyframes glint{0%,100%{opacity:0;transform:scale(.3)}50%{opacity:.9;transform:none}}"]
    for _ in range(n):
        x, y, r = rnd.uniform(20, W - 20), rnd.uniform(20, h - 20), rnd.uniform(3, 6)
        out.append(f'<path class="glint" style="animation-duration:{rnd.uniform(2.4, 4.6):.1f}s;animation-delay:-{rnd.uniform(0, 4):.1f}s" '
                   f'd="M{x:.0f},{y - r:.1f}Q{x:.0f},{y:.0f} {x + r:.1f},{y:.0f}Q{x:.0f},{y:.0f} {x:.0f},{y + r:.1f}'
                   f'Q{x:.0f},{y:.0f} {x - r:.1f},{y:.0f}Q{x:.0f},{y:.0f} {x:.0f},{y - r:.1f}Z" fill="#fff4d6"/>')
    return "".join(out), css


def drift(x0, x1, y, seed):
    """A soft ridge of snow lying along the top edge of a year's grid."""
    rnd = random.Random(seed)
    d, x = [f"M{x0 - 4},{y + 3}"], x0 - 4
    while x < x1 + 4:
        w = rnd.uniform(16, 40)
        d.append(f"q{w / 2:.1f},{-rnd.uniform(6, 11):.1f} {w:.1f},0")
        x += w
    d.append(f"L{x:.1f},{y + 6}L{x0 - 4},{y + 6}Z")
    return "".join(d)


def plate(days, today, total, current, theme):
    C = theme["palette"]
    x0, x1, gap = 56, W - 56, 4.2
    p = (x1 - x0 + gap) / 53
    size = round(p - gap, 2)
    oy0, head, grid, after = 252, 46, 7 * p - gap, 40
    bh = head + grid + after
    yrs = list(range(FIRST_YEAR, today.year + 1))
    last = len(yrs) - 1
    top = sorted(n for k, n in days.items() if k >= f"{FIRST_YEAR}-01-01" and n)[-12]

    def shades(yr):
        """Shade each year against its own busy days, so a quieter year still reads as full."""
        active = sorted(n for k, n in days.items() if k.startswith(str(yr)) and n) or [1]
        q = [active[min(len(active) - 1, int(len(active) * f))] for f in (.25, .5, .75, .92)]
        return lambda n: 0 if n == 0 else 1 + sum(n > t for t in q)

    # the tabby runs each year's lane and wraps at the card's edge; the dots pop in `lag` behind its haunches
    S, v, xs, xe, t0, pause, lag = 1.45, 1250, -90, W + 90, .35, .12, 34
    row_t = (xe - xs) / v
    start = lambda i: t0 + i * (row_t + pause)
    t_w = (today - first_sunday(today.year)).days // 7
    # late in December there's no room left after today, so the tabby hops up onto the year's top edge instead,
    # just short of the year total
    perch = x1 - (x0 + (t_w + 1) * p) < 3 * p
    if perch:
        this_year = sum(n for k, n in days.items() if k.startswith(str(today.year)))
        x_stop = x1 - NUM.width(format(this_year, ","), 30, -0.01) - 116
        t_stop = start(last) + (x_stop - 70 - xs) / v + .42
    else:
        x_stop = (x0 + (t_w + 1) * p + x1) / 2 + 6
        t_stop = start(last) + (x_stop - xs) / v + .12

    def front(i, cx):
        t = start(i) + max(0, cx + lag - xs) / v
        return min(t, t_stop + .05) if i == last else t

    body, css = [], []
    for i, yr in enumerate(yrs):
        hy, gy = oy0 + i * bh, oy0 + i * bh + head
        sun = first_sunday(yr)
        level = shades(yr)
        cols = {}
        day = dt.date(yr, 1, 1)
        while day.year == yr and day <= today:
            n = days.get(day.isoformat(), 0)
            w, r = (day - sun).days // 7, (day.weekday() + 1) % 7
            pawed = n >= top and day != today
            fill = C["now"] if day == today else C["ramp"][4] if n >= top else C["ramp"][level(n) - 1] if n else C["empty"]
            cols.setdefault(w, []).append((pawed, cell(round(x0 + w * p, 2), round(gy + r * p, 2), size, fill,
                                                       C["ground"] if pawed else None)))
            day += dt.timedelta(1)
        for w, cells in cols.items():
            dl = front(i, x0 + w * p + size / 2)
            body.append(f'<g class="dot" style="animation-delay:{dl:.3f}s">{"".join(c for pw, c in cells if not pw)}</g>')
            paws = "".join(c for pw, c in cells if pw)
            if paws:
                body.append(f'<g class="dotpaw" style="animation-delay:{dl + .06:.3f}s">{paws}</g>')
        now = i == last
        year_total = sum(n for k, n in days.items() if k.startswith(str(yr)))
        tone = C["ink"] if now else C["muted"]
        hb = hy + 30
        left = f'<path d="{NUM.path(str(yr), x0, hb, 30, -0.01)}" fill="{tone}"/>'
        right = f'<path d="{NUM.path(format(year_total, ","), x1, hb, 30, -0.01, "end")}" fill="{tone}"/>'
        body.append(f'<g class="fade" style="animation-delay:{front(i, x0 + 80):.2f}s">{left}</g>')
        body.append(f'<g class="fade" style="animation-delay:{t_stop + .2 if now else front(i, x1):.2f}s">{right}</g>')
        ledge, shown = theme["ledge"], f'class="fade" style="animation-delay:{front(i, x0):.2f}s"'
        if "snow" in ledge:
            body.append(f'<path {shown} d="{drift(x0, x1, gy - 5, yr)}" fill="#e9f3fd" opacity=".92"/>')
        if "leaves" in ledge:
            body.append(f'<g {shown}>{litter(x0, x1, gy - 2, yr)}</g>')
        if "lights" in ledge:
            # strung between the year and its total so the wire never crosses the numbers
            body.append(f'<g {shown}>{lights(x0 + NUM.width(str(yr), 30) + 28, x1 - NUM.width(format(year_total, ","), 30) - 28, gy - 19, yr, theme["bulbs"])}</g>')
    css.append(".dot{transform-box:fill-box;transform-origin:50% 50%;animation:dot .42s cubic-bezier(.2,.9,.3,1.35) both}"
               "@keyframes dot{from{opacity:0;transform:translate(-18px,4px) scale(.4)}}"
               ".dotpaw{transform-box:fill-box;transform-origin:50% 50%;animation:dotpaw .6s cubic-bezier(.2,.9,.3,1.6) both}"
               "@keyframes dotpaw{from{opacity:0;transform:scale(.2) rotate(-25deg)}}"
               ".fade{animation:fade .45s ease-out both}@keyframes fade{from{opacity:0}}")
    last_bottom = oy0 + last * bh + head + grid
    for m in range(1, 13):
        first = dt.date(today.year, m, 1)
        body.append(label(first.strftime("%b"), x0 + (first - first_sunday(today.year)).days // 7 * p,
                          last_bottom + 34, 16, C["faint"]))

    # the tabby stops in this year's unwritten days, looks back at the dots, then turns to face us
    t_look, t_turn = t_stop + .3, t_stop + 1.55
    T = t_turn + .5
    pct = lambda t: f"{t / T * 100:.3f}%"
    rest = oy0 + last * bh + head - 3 if perch else last_bottom
    keys = []
    for i in range(len(yrs)):
        ground = oy0 + i * bh + head + grid
        keys.append((start(i), xs, ground, "linear"))
        if i < last:
            keys.append((start(i) + row_t, xe, ground, "linear"))
            keys.append((start(i) + row_t + .001, xs, ground + bh, "linear"))
        elif perch:
            t_hop = start(i) + (x_stop - 70 - xs) / v
            keys.append((t_hop, x_stop - 70, ground, "linear"))
            keys += [(t_hop + .42 * f, x_stop - 70 * (1 - f), ground + (rest - ground) * f - 46 * math.sin(math.pi * f), "linear")
                     for f in (j / 8 for j in range(1, 9))]
        else:
            keys.append((start(i) + (x_stop - 70 - xs) / v, x_stop - 70, ground, "cubic-bezier(.2,.6,.35,1)"))
            keys.append((t_stop, x_stop, ground, "linear"))
    frames = "".join(f"{pct(t)}{{transform:translate({x:.1f}px,{y:.1f}px) scale({S});animation-timing-function:{e}}}"
                     for t, x, y, e in keys)
    css.append(f".tab{{transform:translate({x_stop:.1f}px,{rest:.1f}px) scale({S});animation:tab {T:.3f}s both}}"
               f"@keyframes tab{{0%{{transform:translate({xs}px,{oy0 + head + grid:.1f}px) scale({S})}}{frames}}}")
    scarf = theme["scarf"]
    hat = theme["hat"]
    rsvg, rcss = vcats.tabby_run("tr", scarf=scarf, hat=hat)
    ssvg, scss = vcats.tabby_stand("ts", look_at=t_look, look_back=.22, scarf=scarf, hat=hat)
    fsvg, fcss = vcats.tabby_front("tf", delay=t_turn, scarf=scarf, hat=hat)
    css += rcss + scss + fcss
    css.append(f".tab-run{{opacity:0;animation:tabrun {T:.3f}s steps(1,end) both}}"
               f"@keyframes tabrun{{0%{{opacity:1}}{pct(t_stop)}{{opacity:0}}}}"
               f".tab-stand{{opacity:0;animation:tabstand {T:.3f}s both}}"
               f"@keyframes tabstand{{0%,{pct(t_stop - .001)}{{opacity:0;transform:none}}{pct(t_stop)}{{opacity:1;transform:none}}"
               f"{pct(t_turn)}{{opacity:1;transform:none;animation-timing-function:cubic-bezier(.5,0,1,1)}}"
               f"{pct(t_turn + .12)}{{opacity:1;transform:scale(.08,1)}}{pct(t_turn + .121)}{{opacity:0}}100%{{opacity:0}}}}"
               f".tab-front{{animation:tabfront {T:.3f}s both}}"
               f"@keyframes tabfront{{0%,{pct(t_turn + .12)}{{opacity:0;transform:scale(.08,1)}}"
               f"{pct(t_turn + .121)}{{opacity:1;transform:scale(.08,1);animation-timing-function:cubic-bezier(.2,.9,.3,1.25)}}"
               f"100%{{opacity:1;transform:none}}}}")
    body.append(f'<g class="tab"><g class="tab-run">{rsvg}</g><g class="tab-stand">{ssvg}</g>'
                f'<g class="tab-front">{fsvg}</g></g>')

    # the gray cat joins late, chases along this year's top edge, gives up and flops down asleep
    G, gv = 1.25, 900
    g_edge = oy0 + last * bh + head + 1
    g_in = start(last) + .45
    g_x = x0 + 30 * p
    g_stop = g_in + (g_x - xs) / gv + .18
    settle = theme["settle"]
    gray_nap = vcats.gray_sleep("gs", settle=(settle, g_stop + 1.2) if settle else None)
    css += vcats.gray_run("gr")[1] + gray_nap[1]
    css.append(f".gry{{transform:translate({g_x:.1f}px,{g_edge:.1f}px) scale({G});animation:gry {T:.3f}s linear both}}"
               f"@keyframes gry{{0%,{pct(g_in)}{{transform:translate({xs}px,{g_edge:.1f}px) scale({G})}}"
               f"{pct(g_in + (g_x - 60 - xs) / gv)}{{transform:translate({g_x - 60:.1f}px,{g_edge:.1f}px) scale({G});"
               f"animation-timing-function:cubic-bezier(.2,.6,.35,1)}}"
               f"{pct(g_stop)}{{transform:translate({g_x:.1f}px,{g_edge:.1f}px) scale({G})}}}}"
               f".gry-run{{opacity:0;animation:gryrun {T:.3f}s steps(1,end) both}}"
               f"@keyframes gryrun{{0%{{opacity:1}}{pct(g_stop)}{{opacity:0}}}}"
               f".gry-nap{{animation:grynap {T:.3f}s both}}"
               f"@keyframes grynap{{0%,{pct(g_stop)}{{opacity:0;transform:scale(-1.08,.8)}}"
               f"{pct(g_stop + .001)}{{opacity:1;transform:scale(-1.08,.8);animation-timing-function:cubic-bezier(.2,.9,.3,1.3)}}"
               f"{pct(g_stop + .35)}{{transform:scale(-1,1)}}100%{{opacity:1;transform:scale(-1,1)}}}}")
    body.append(f'<g class="gry"><g class="gry-run">{vcats.gray_run("gr")[0]}</g>'
                f'<g class="gry-nap" style="transform:scale(-1,1)">{gray_nap[0]}</g></g>')
    zx, zy = g_x + 8, g_edge - 38
    body.append("".join(f'<path class="zz zz{i}" d="{PIX.path("z", zx + i * 9, zy - i * 11, 15 + i * 4)}" '
                        f'fill="{C["muted"]}"/>' for i in range(3)))
    css.append(f".zz{{opacity:0;animation:zz 3.6s linear infinite}}.zz0{{animation-delay:{g_stop + .5:.2f}s}}"
               f".zz1{{animation-delay:{g_stop + 1.7:.2f}s}}.zz2{{animation-delay:{g_stop + 2.9:.2f}s}}"
               "@keyframes zz{0%{opacity:0;transform:translate(0,0)}20%{opacity:.9}80%{opacity:.9}"
               "100%{opacity:0;transform:translate(6px,-14px)}}")
    h = round(last_bottom + 70)
    weather = {"snow": lambda: snowfall(h), "light snow": lambda: snowfall(h, 30, (1.2, 1.6, 2.2, 2.8)),
               "flurries": lambda: snowfall(h, 14, (1.2, 1.6, 2)), "leaves": lambda: leaffall(h),
               "sparkles": lambda: sparkles(h)}
    for kind in theme["falling"]:
        layer, wcss = weather[kind]()
        body.append(layer)
        css += wcss
    if "lights" in theme["ledge"]:
        css.append(".bulb{animation:twinkle ease-in-out infinite alternate}@keyframes twinkle{from{opacity:.45}to{opacity:1}}")
    return header(C, total, current) + "".join(body), css, h


def build(out):
    days = load_days()
    today = dt.date.fromisoformat(max(days))
    total = last_year()["total"]
    current = streaks(days)["current"]["length"]
    name, theme = themes.pick(today)
    C = theme["palette"]
    body, css, h = plate(days, today, total, current, theme)
    title = (f"{total:,} contributions in the last year; current streak {current} days; longest streak {RECORD:,} days. "
             "Every year since 2023 as a contribution grid, filling in behind a running orange tabby, "
             "with a gray cat chasing it.")
    style = "\n".join(css + ["@media (prefers-reduced-motion:reduce){*{animation:none!important}}"])
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {h}" width="{W}" height="{h}" role="img">'
           f"<title>{title}</title><style>{style}</style>"
           f'<rect width="{W}" height="{h}" rx="20" fill="{C["ground"]}"/>'
           f'<rect x=".5" y=".5" width="{W - 1}" height="{h - 1}" rx="19.5" fill="none" stroke="{C["line"]}"/>'
           f"{body}</svg>")
    Path(out).parent.mkdir(parents=True, exist_ok=True)
    Path(out).write_text(svg)
    return name
