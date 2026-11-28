"""The contributions plate: every year since 2023 as a paw grid, with the cats chasing through it."""
import datetime as dt
from pathlib import Path

import vcats
from common import face, last_year, load_days, streaks

W = 1200
RECORD = 1007
FIRST_YEAR = 2023
C = {
    "ground": "#0a110d", "line": "#1c2b22", "ink": "#ece6d6", "muted": "#8b9a8f", "faint": "#56665a",
    "empty": "#121c16", "now": "#ff9d4a",
    "ramp": ["#1b3a26", "#25603a", "#3a9149", "#76c25f", "#c6ec86"],
}
NUM = face("Geist[wght].ttf", wght=620)
NUM_L = face("Geist[wght].ttf", wght=480)
PIX = face("DepartureMono-Regular.otf")
PAW = ["..#.#..", "#.....#", "...#...", ".#####.", ".#####.", "..###.."]


def label(text, x, y, size=22, fill=None, anchor="start", track=0.04):
    return f'<path d="{PIX.path(text.upper(), x, y, size, track, anchor)}" fill="{fill or C["muted"]}"/>'


def paw(x, y, s):
    return "".join(f"M{x + i * s:g},{y + j * s:g}h{s}v{s}h-{s}z"
                   for j, row in enumerate(PAW) for i, ch in enumerate(row) if ch == "#")


def cell(x, y, size, fill, pawed=False, r=4):
    out = f'<rect x="{x}" y="{y}" width="{size}" height="{size}" rx="{r}" fill="{fill}"/>'
    if pawed:
        s = 2 if size >= 16 else 1.6
        out += f'<path d="{paw(x + (size - 7 * s) / 2, y + (size - 6 * s) / 2 + .5, s)}" fill="{C["ground"]}"/>'
    return out


def header(total, current):
    out = [f'<path d="{NUM.path(format(total, ","), 56, 148, 112, -0.02)}" fill="{C["ink"]}"/>',
           label("contributions in the last year", 60, 194, 24)]
    x = W - 56
    for big, cap in reversed([(str(current), "current streak"), (format(RECORD, ","), "longest streak")]):
        uw = NUM_L.width(" days", 30)
        out.append(f'<path d="{NUM_L.path(" days", x, 148, 30, 0, "end")}" fill="{C["muted"]}"/>')
        out.append(f'<path d="{NUM.path(big, x - uw, 148, 56, -0.02, "end")}" fill="{C["ink"]}"/>')
        out.append(label(cap, x, 194, 20, anchor="end"))
        x -= max(NUM.width(big, 56, -0.02) + uw, PIX.width(cap.upper(), 20, .04)) + 56
    return "".join(out)


def first_sunday(year):
    jan1 = dt.date(year, 1, 1)
    return jan1 - dt.timedelta((jan1.weekday() + 1) % 7)


def plate(days, today, total, current):
    x0, x1, gap = 56, W - 56, 4.2
    p = (x1 - x0 + gap) / 53
    size = round(p - gap, 2)
    oy0, head, grid, after = 252, 46, 7 * p - gap, 40
    bh = head + grid + after
    yrs = list(range(FIRST_YEAR, today.year + 1))
    last = len(yrs) - 1
    active = sorted(n for k, n in days.items() if k >= f"{FIRST_YEAR}-01-01" and n)
    q = [active[int(len(active) * f)] for f in (.25, .5, .75, .92)]
    level = lambda n: 0 if n == 0 else 1 + sum(n > t for t in q)
    top = active[-12]

    # the tabby runs each year's lane and wraps at the card's edge; the dots pop in `lag` behind its haunches
    S, v, xs, xe, t0, pause, lag = 1.45, 1250, -90, W + 90, .35, .12, 34
    row_t = (xe - xs) / v
    start = lambda i: t0 + i * (row_t + pause)
    t_w = (today - first_sunday(today.year)).days // 7
    x_stop = (x0 + (t_w + 1) * p + x1) / 2 + 6
    t_stop = start(last) + (x_stop - xs) / v + .12

    def front(i, cx):
        t = start(i) + max(0, cx + lag - xs) / v
        return min(t, t_stop + .05) if i == last else t

    body, css = [], []
    for i, yr in enumerate(yrs):
        hy, gy = oy0 + i * bh, oy0 + i * bh + head
        sun = first_sunday(yr)
        cols = {}
        day = dt.date(yr, 1, 1)
        while day.year == yr and day <= today:
            n = days.get(day.isoformat(), 0)
            w, r = (day - sun).days // 7, (day.weekday() + 1) % 7
            pawed = n >= top and day != today
            fill = C["now"] if day == today else C["ramp"][4] if n >= top else C["ramp"][level(n) - 1] if n else C["empty"]
            cols.setdefault(w, []).append((pawed, cell(round(x0 + w * p, 2), round(gy + r * p, 2), size, fill, pawed)))
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
    keys = []
    for i in range(len(yrs)):
        ground = oy0 + i * bh + head + grid
        keys.append((start(i), xs, ground, "linear"))
        if i < last:
            keys.append((start(i) + row_t, xe, ground, "linear"))
            keys.append((start(i) + row_t + .001, xs, ground + bh, "linear"))
        else:
            keys.append((start(i) + (x_stop - 70 - xs) / v, x_stop - 70, ground, "cubic-bezier(.2,.6,.35,1)"))
            keys.append((t_stop, x_stop, ground, "linear"))
    frames = "".join(f"{pct(t)}{{transform:translate({x:.1f}px,{y:.1f}px) scale({S});animation-timing-function:{e}}}"
                     for t, x, y, e in keys)
    css.append(f".tab{{transform:translate({x_stop:.1f}px,{last_bottom:.1f}px) scale({S});animation:tab {T:.3f}s both}}"
               f"@keyframes tab{{0%{{transform:translate({xs}px,{oy0 + head + grid:.1f}px) scale({S})}}{frames}}}")
    rsvg, rcss = vcats.tabby_run("tr")
    ssvg, scss = vcats.tabby_stand("ts", look_at=t_look, look_back=.22)
    fsvg, fcss = vcats.tabby_front("tf", delay=t_turn)
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
    css += vcats.gray_run("gr")[1] + vcats.gray_sleep("gs")[1]
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
                f'<g class="gry-nap" style="transform:scale(-1,1)">{vcats.gray_sleep("gs")[0]}</g></g>')
    zx, zy = g_x + 8, g_edge - 38
    body.append("".join(f'<path class="zz zz{i}" d="{PIX.path("z", zx + i * 9, zy - i * 11, 15 + i * 4)}" '
                        f'fill="{C["muted"]}"/>' for i in range(3)))
    css.append(f".zz{{opacity:0;animation:zz 3.6s linear infinite}}.zz0{{animation-delay:{g_stop + .5:.2f}s}}"
               f".zz1{{animation-delay:{g_stop + 1.7:.2f}s}}.zz2{{animation-delay:{g_stop + 2.9:.2f}s}}"
               "@keyframes zz{0%{opacity:0;transform:translate(0,0)}20%{opacity:.9}80%{opacity:.9}"
               "100%{opacity:0;transform:translate(6px,-14px)}}")
    return header(total, current) + "".join(body), css, round(last_bottom + 70)


def build(out):
    days = load_days()
    today = dt.date.fromisoformat(max(days))
    total = last_year()["total"]
    current = streaks(days)["current"]["length"]
    body, css, h = plate(days, today, total, current)
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
