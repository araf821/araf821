"""Desk-cat choreography for the one-bit desktop: each act is keyframed paths plus pose changes, compiled to CSS."""
import pixels as px_

CAT_SIT = ["..#..........#..", "..##........##..", "..#o#......#o#..", "..#oo######oo#..",
           "..#oooooooooo#..", ".#oo#oooooo#oo#.", ".#oo#oooooo#oo#.", ".#ooooo##ooooo#.",
           "..#oooooooooo#..", "...##oooooo##...", "...#oooooooo#.##", "..#oooooooooo#.#",
           "..#oooooooooo##.", "..#oo#oooo#oo#..", "..#oo#oooo#oo#..", "..############.."]
CAT_PAW = CAT_SIT[:10] + ["...#oooooooo###.", "..#ooooooooo#oo#", "..#oooooooooo##."] + CAT_SIT[13:]
CAT_WALK_A = ["............#.#.", "............###.", "#..........#ooo#", "#..........#o#o#",
              ".#.#########ooo#", ".##ooooooooooo#.", "..#oooooooooo#..", "..#oooooooooo#..",
              "..#oo######oo#..", "..#o#......#o#..", ".#o#........#o#.", ".##..........##."]
CAT_WALK_B = CAT_WALK_A[:9] + ["...#o#....#o#...", "...#o#....#o#...", "...##......##..."]
CAT_SLEEP_A = [".#.#............", ".###..#######...", "#ooo##ooooooo##.", "#oooooooooooooo#",
               "#o##ooooooooooo#", "#oooooooooooooo#", ".#oo#######ooo#.", "..##.......###.."]
CAT_SLEEP_B = [".#.#...#####....", ".###..#ooooo#...", "#ooo##ooooooo##.", "#oooooooooooooo#",
               "#o##ooooooooooo#", "#oooooooooooooo#", ".#oo#######ooo#.", "..##.......###.."]
CURSOR = ["#.........", "##........", "#o#.......", "#oo#......", "#ooo#.....", "#oooo#....",
          "#ooooo#...", "#oooooo#..", "#ooooooo#.", "#oooooooo#", "#oooo#####", "#oo#oo#...",
          "#o#.#oo#..", "##...#oo#.", ".....#oo#.", "......##.."]
MUG = [".#######..", ".#ooooo#..", ".#ooooo###", ".#ooooo#.#", ".#ooooo#.#", ".#ooooo###",
       ".#ooooo#..", "..#####..."]

# Stripes for the orange tabby: forehead marks and a striped back on every pose
_SIT_S = [(6, 4), (8, 4), (10, 4), (4, 11), (7, 11), (10, 11), (5, 12), (8, 12), (11, 12)]
_WALK_S = [(13, 2), (5, 5), (8, 5), (11, 5), (4, 6), (7, 6), (10, 6), (5, 7), (8, 7), (11, 7)]
_SLEEP_S = [(2, 2), (8, 2), (10, 2), (12, 2), (7, 3), (10, 3), (13, 3), (6, 5), (9, 5), (12, 5)]

# A skin: pose -> (frames, seconds per frame cycle), plus sprite scale and width in sprite pixels
SKINS = {
    "desk": {"s": 3, "w": 16, "poses": {
        "walk": ([CAT_WALK_A, CAT_WALK_B], .3), "sit": ([CAT_SIT], 0), "paw": ([CAT_PAW], 0),
        "sleep": ([CAT_SLEEP_A, CAT_SLEEP_B], 3.2)}},
    "orange": {"s": 3, "w": 16, "poses": {
        "walk": ([px_.tabby(CAT_WALK_A, _WALK_S), px_.tabby(CAT_WALK_B, _WALK_S)], .3),
        "run": ([px_.tabby(CAT_WALK_A, _WALK_S), px_.tabby(CAT_WALK_B, _WALK_S)], .12),
        "sit": ([px_.tabby(CAT_SIT, _SIT_S)], 0), "paw": ([px_.tabby(CAT_PAW, _SIT_S)], 0),
        "sleep": ([px_.tabby(CAT_SLEEP_A, _SLEEP_S), px_.tabby(CAT_SLEEP_B, _SLEEP_S)], 3.2)}},
    "gray": {"s": 3, "w": 24, "poses": {
        "walk": ([px_.fat_walk(0), px_.fat_walk(1)], .5), "sit": ([px_.fat_sit()], 0),
        "paw": ([px_.fat_sit(True)], 0), "sleep": ([px_.fat_sleep(0), px_.fat_sleep(1)], 3.6)}},
    "cloud": {"s": 3, "w": 32, "poses": {"fight": ([px_.cloud(0), px_.cloud(2.1), px_.cloud(4.2)], .42)}},
    "cursor": {"s": 1, "w": 10, "poses": {"arrow": ([CURSOR], 0)}},
    "tail": {"s": 3, "w": 7, "poses": {"flick": (px_.TAIL, 1.4)}},
}
HOP_UP, HOP_DOWN = "cubic-bezier(.2,.7,.4,1)", "cubic-bezier(.6,0,.8,.4)"


def fills(k, palette):
    """Fill per sprite code. One-bit: gray is a dither, orange is white fur with ink tabby stripes."""
    t = k["t"]
    base = {"#": t["ink"], "o": t["paper"], "w": t["paper"]}
    if palette == "colour":
        return {**base, "g": t["gray"], "w": t["eye"], "q": t["orange"], "s": t["stripe"]}
    return {**base, "g": "url(#dither)", "q": t["paper"], "s": t["ink"]}


def pix(rows, fill, s, PX, anchor="feet"):
    """One path per sprite code, horizontal runs; feet on y=0 or top-left at the origin."""
    top = -len(rows) * s if anchor == "feet" else 0
    paths = {}
    for j, row in enumerate(rows):
        i = 0
        while i < len(row):
            c = row[i]
            k = i
            while k < len(row) and row[k] == c:
                k += 1
            if c != ".":
                paths.setdefault(c, []).append(
                    f"M{i * s * PX:g},{(top + j * s) * PX:g}h{(k - i) * s * PX:g}v{s * PX:g}h-{(k - i) * s * PX:g}z")
            i = k
    order = [c for c in ("o", "w", "q", "g", "s", "#") if c in paths]
    return "".join(f'<path d="{"".join(paths[c])}" fill="{fill[c]}"/>' for c in order)


class Act:
    """A sprite group's path (translate, optional mirror) and pose timeline over one run of T seconds."""

    def __init__(self, name, kit, skin="desk", palette="bit", anchor="feet"):
        self.name, self.k, self.skin = name, kit, SKINS[skin]
        self.s, self.w = self.skin["s"], self.skin["w"]
        self.fill, self.anchor = fills(kit, palette), anchor
        self.keys, self.poses = [], []

    def at(self, t, x, y, flip=False, ease="linear"):
        self.keys.append((t, x, y, flip, ease))
        return self

    def pose(self, t, p):
        self.poses.append((t, p))
        return self

    def walk(self, t0, t1, x0, x1, y, gait="walk"):
        flip = x1 < x0
        return self.pose(t0, gait).at(t0, x0, y, flip).at(t1, x1, y, flip)

    def hop(self, t0, t1, a, b, lift=26, flip=False):
        top = min(a[1], b[1]) - lift
        return (self.at(t0, *a, flip, HOP_UP).at((t0 + t1) / 2, (a[0] + b[0]) / 2, top, flip, HOP_DOWN)
                .at(t1, *b, flip))

    def end(self):
        return max([k[0] for k in self.keys] + [p[0] for p in self.poses])

    def last(self):
        return sorted(self.keys, key=lambda k: k[0])[-1][1:3]

    def _tf(self, x, y, flip):
        PX = self.k["PX"]
        if flip:
            return f"translate({(x + self.w * self.s) * PX:g}px,{y * PX:g}px) scale(-1,1)"
        return f"translate({x * PX:g}px,{y * PX:g}px)"

    def used(self):
        return sorted({p for _, p in self.poses if p != "none"})

    def css(self, T):
        keys = sorted(self.keys, key=lambda k: k[0])
        turned = []
        for a, b in zip(keys, keys[1:]):
            if a[3] != b[3]:
                turned.append((max(a[0], b[0] - .02), b[1], b[2], a[3], "linear"))
        keys = sorted(keys + turned, key=lambda k: k[0])
        frames = "".join(f"{t / T * 100:.3f}%{{transform:{self._tf(x, y, f)};animation-timing-function:{e}}}"
                         for t, x, y, f, e in keys)
        out = [f".{self.name}{{transform:{self._tf(*keys[-1][1:4])};animation:{self.name}-path {T}s both}}",
               f"@keyframes {self.name}-path{{{frames}}}"]
        seq = sorted(self.poses)
        final = seq[-1][1]
        for n in self.used():
            fr = [f"{t / T * 100:.3f}%{{opacity:{int(p == n)}}}" for t, p in seq]
            if seq[0][0] > 0:
                fr.insert(0, f"0%{{opacity:{int(seq[0][1] == n)}}}")
            out.append(f".{self.name} .{n}{{opacity:{int(n == final)};animation:{self.name}-{n} {T}s steps(1,end) both}}")
            out.append(f"@keyframes {self.name}-{n}{{{''.join(fr)}}}")
            sprites, cycle = self.skin["poses"][n]
            for i in range(len(sprites) if len(sprites) > 1 else 0):
                out.append(f".{self.name} .{n} .fr{i}{{animation:cyc{len(sprites)}-{i} {cycle}s steps(1,end) infinite}}")
        return out

    def svg(self):
        groups = []
        for n in self.used():
            sprites, _ = self.skin["poses"][n]
            inner = "".join(f'<g class="fr fr{i}">{pix(r, self.fill, self.s, self.k["PX"], self.anchor)}</g>'
                            for i, r in enumerate(sprites))
            groups.append(f'<g class="{n}">{inner}</g>')
        return f'<g class="{self.name} mover">{"".join(groups)}</g>'


def zzz(k, x, y, T, scale=1):
    t = k["t"]
    marks = "".join(f'<path class="z z{i}" d="{k["text"]("Z", x + i * 7 * scale, y - i * 9 * scale, scale)}" fill="{t["ink"]}"/>'
                    for i in range(3))
    css = [f".z0{{animation-delay:{T + .6:g}s}}.z1{{animation-delay:{T + 1.8:g}s}}.z2{{animation-delay:{T + 3:g}s}}"]
    return marks, css


def common_css(T, k):
    PX = k["PX"]
    cyc = []
    for n in (2, 3, 7):
        for i in range(n):
            steps = "".join(f"{j / n * 100:.2f}%{{opacity:{int(i == j)}}}" for j in range(n))
            cyc.append(f"@keyframes cyc{n}-{i}{{{steps}100%{{opacity:{int(i == n - 1)}}}}}")
    return cyc + [
        ".fr{opacity:0}.fr0{opacity:1}",
        ".z{opacity:0;animation:z 3.6s linear infinite}",
        f"@keyframes z{{0%{{opacity:0;transform:translate(0,0)}}15%{{opacity:1}}70%{{opacity:1}}"
        f"100%{{opacity:0;transform:translate(0,-{6 * PX:g}px)}}}}",
    ]


REDUCED = ("@media (prefers-reduced-motion:reduce){.ants,.mover,.mover *,.z,.fx,.fx *{animation:none!important}"
           ".fr{opacity:0}.fr0{opacity:1}.z{opacity:1}}")


def jiggle(t0, T):
    """Shake the Last Year window when something heavy lands on it."""
    p = lambda t: f"{t / T * 100:.2f}%"
    return [f".lastwin{{animation:jiggle {T}s both}}",
            f"@keyframes jiggle{{0%,{p(t0)}{{transform:none}}{p(t0 + .06)}{{transform:translate(0,5px)}}"
            f"{p(t0 + .14)}{{transform:translate(0,-3px)}}{p(t0 + .22)}{{transform:translate(0,2px)}}"
            f"{p(t0 + .3)},100%{{transform:none}}}}"]


# ---------------------------------------------------------------------------- one cat
# L: layout of the base scene (screen px). k: drawing kit from onebit.py.

def nap(L, k, palette="bit"):
    cat = Act("cat", k)
    perch = (L["rx"] + L["rw"] - 84, L["ry"])
    cat.at(0, -56, 326).walk(0.5, 3.0, -56, 270, 326).pose(3.0, "sit")
    cat.hop(3.7, 4.3, (270, 326), perch).at(5.0, *perch).pose(5.0, "sleep")
    T = cat.end()
    marks, zc = zzz(k, perch[0] + 4, perch[1] - 34, T)
    return cat.svg() + marks, cat.css(T) + zc, T, "a pixel cat walks in and falls asleep on top of the Last Year window"


def keyboard(L, k, palette="bit"):
    t = k["t"]
    nx, ny, nw, nh = 14, 182, 172, 64
    mash = "SSSDDDFFFFGGGHHHJJJJKKKLL"
    note = (k["window"](nx, ny, nw, nh, "README", False)
            + f'<path d="{k["text"]("# ARAF", nx + 8, ny + 18)}" fill="{t["ink"]}"/>'
            + f'<g class="fx typed"><path d="{k["text"](mash, nx + 8, ny + 30)}" fill="{t["ink"]}"/></g>')
    cat = Act("cat", k)
    cat.at(0, -56, 326).walk(0.6, 3.4, -56, 236, 326).pose(3.4, "sit")
    T = cat.end()
    css = cat.css(T) + [
        f".typed{{clip-path:inset(-20% 0 -20% 0);animation:typed 2.6s steps({len(mash)}) .8s both}}",
        "@keyframes typed{from{clip-path:inset(-20% 100% -20% 0)}to{clip-path:inset(-20% 0 -20% 0)}}",
    ]
    return note + cat.svg(), css, T, "a pixel cat walks across the keyboard and types gibberish into a README"


def chase(L, k, palette="bit"):
    cur = Act("cursor", k, "cursor", anchor="top").pose(0, "arrow")
    for tt, x, y in [(0, 300, 250), (0.8, 110, 300), (1.4, 330, 310), (2.2, 120, 196), (3.2, 150, 318)]:
        cur.at(tt, x, y, ease="cubic-bezier(.3,0,.2,1)")
    cat = Act("cat", k)
    cat.at(0, 40, 326).pose(0, "sit").at(1.0, 40, 326)
    cat.walk(1.0, 2.3, 40, 290, 326).walk(2.4, 3.4, 290, 170, 326)
    cat.hop(3.5, 3.9, (170, 326), (128, 326), lift=22, flip=True).pose(3.9, "sit")
    cat.at(4.8, 128, 326, True).pose(4.8, "sleep")
    T = cat.end()
    marks, zc = zzz(k, 160, 292, T)
    return cur.svg() + cat.svg() + marks, cur.css(T) + cat.css(T) + zc, T, \
        "a pixel cat chases the mouse cursor, pounces on it and falls asleep on top of it"


def stairs(L, k, palette="bit"):
    SKINS["desk1"] = {**SKINS["desk"], "s": 1}
    cat = Act("cat", k, "desk1")
    bars, ry = L["bars"], L["ry"]
    cat.at(0, 360, ry).at(0.4, 360, ry).walk(0.4, 2.0, 360, 204, ry)
    first = (bars[0][0] - 2, bars[0][1])
    cat.hop(2.1, 2.6, (204, ry), first, lift=10).pose(2.1, "sit")
    tt, prev = 2.6, first
    for x, top in bars[1:]:
        nxt = (x - 2, top)
        cat.hop(tt + 0.08, tt + 0.38, prev, nxt, lift=8)
        tt, prev = tt + 0.38, nxt
    cat.pose(tt, "sit").at(tt + 0.8, *prev).pose(tt + 0.8, "sleep")
    T = cat.end()
    marks, zc = zzz(k, prev[0] + 2, prev[1] - 18, T)
    return cat.svg() + marks, cat.css(T) + zc, T, \
        "a pixel cat climbs the monthly bars like stairs and falls asleep on top of the latest month"


def mug(L, k, palette="bit"):
    PX, ry = k["PX"], L["ry"]
    mx = L["rx"] + L["rw"] - 50
    cup = f'<g class="fx mug">{pix(MUG, fills(k, palette), 2, PX)}</g>'
    cat = Act("cat", k)
    perch = (mx - 52, ry)
    cat.at(0, -56, 326).walk(0.4, 2.6, -56, 250, 326).pose(2.6, "sit")
    cat.hop(3.1, 3.7, (250, 326), perch).pose(3.7, "sit").at(4.4, *perch)
    cat.pose(4.4, "paw").pose(4.7, "sit").pose(5.0, "paw").pose(5.4, "sit").at(6.6, *perch)
    T = cat.end()
    p = lambda x, y, r=0: f"translate({x * PX:g}px,{y * PX:g}px) rotate({r}deg)"
    css = cat.css(T) + [
        f".mug{{transform:{p(mx + 30, 380, 140)};transform-box:fill-box;transform-origin:center;"
        f"animation:mug {T}s both}}",
        f"@keyframes mug{{0%,{4.45 / T * 100:.2f}%{{transform:{p(mx, ry)}}}"
        f"{4.6 / T * 100:.2f}%{{transform:{p(mx + 4, ry, 6)}}}{4.75 / T * 100:.2f}%{{transform:{p(mx + 2, ry)}}}"
        f"{5.05 / T * 100:.2f}%{{transform:{p(mx + 2, ry)};animation-timing-function:ease-out}}"
        f"{5.35 / T * 100:.2f}%{{transform:{p(mx + 22, ry, 20)};animation-timing-function:cubic-bezier(.5,0,.9,.5)}}"
        f"100%{{transform:{p(mx + 30, 380, 140)}}}}}",
    ]
    return cup + cat.svg(), css, T, "a pixel cat hops onto a window and pushes a coffee mug off the edge"


def folder(L, k, palette="bit"):
    t = k["t"]
    fx, fy, fw, fh = 14, 186, 172, 116
    win = (k["window"](fx, fy, fw, fh, "NEW FOLDER", False)
           + f'<path d="{k["rect"](fx + 1, fy + 24, fw - 2, 1)}" fill="{t["ink"]}"/>'
           + f'<g class="fx empty"><path d="{k["text"]("0 ITEMS", fx + 8, fy + 15)}" fill="{t["ink"]}"/></g>'
           + f'<g class="fx full"><path d="{k["text"]("1 ITEM", fx + 8, fy + 15)}" fill="{t["ink"]}"/></g>')
    cat = Act("cat", k)
    inside = (fx + 60, fy + fh - 10)
    cat.at(0, -56, 326).walk(0.4, 1.9, -56, 50, 326).pose(1.9, "sit")
    cat.hop(2.5, 3.1, (50, 326), inside, lift=40).pose(3.1, "sit").at(3.9, *inside).pose(3.9, "sleep")
    T = cat.end()
    marks, zc = zzz(k, inside[0] + 4, inside[1] - 34, T)
    sw = 3.05 / T * 100
    css = cat.css(T) + zc + [
        f".empty{{opacity:0;animation:empty {T}s steps(1,end) both}}@keyframes empty{{0%{{opacity:1}}{sw:.2f}%{{opacity:0}}}}",
        f".full{{animation:full {T}s steps(1,end) both}}@keyframes full{{0%{{opacity:0}}{sw:.2f}%{{opacity:1}}}}",
    ]
    return win + cat.svg() + marks, css, T, "a pixel cat climbs into an empty folder window and falls asleep in it"


# ---------------------------------------------------------------------------- two cats
# The gray one is heavy (slow waddle, short hops); the orange one is a tabby and fast.

def brawl(L, k, palette="bit"):
    ry = L["ry"]
    oc, gc, cl = Act("oc", k, "orange", palette), Act("gc", k, "gray", palette), Act("cl", k, "cloud", palette)
    o_perch, g_perch = (L["rx"] + L["rw"] - 66, ry), (L["rx"] + 64, ry)
    oc.at(0, *o_perch).pose(0, "sit").pose(3.4, "paw").pose(3.6, "sit").pose(3.9, "paw").pose(4.1, "sit")
    gc.at(0, -80, 326).walk(0.3, 3.2, -80, 210, 326).pose(3.2, "sit")
    gc.at(3.9, 210, 326, ease=HOP_UP).at(4.15, 222, 236, ease=HOP_DOWN).at(4.4, 228, 326)   # too heavy: falls short
    gc.pose(4.4, "sit").hop(5.0, 5.6, (228, 326), g_perch, lift=36).pose(5.6, "sit")
    oc.pose(6.0, "paw").at(6.2, *o_perch).pose(6.25, "none")
    gc.at(6.25, *g_perch).pose(6.25, "none")
    mid = (g_perch[0] + 30, ry + 6)
    cl.at(0, *mid).pose(0, "none").at(6.2, *mid).pose(6.25, "fight")
    for i, dx in enumerate((-14, 12, -10, 16, -6, 8, 0)):
        cl.at(6.45 + i * .26, mid[0] + dx, mid[1] - (6 if i % 2 else 0))
    cl.pose(8.3, "none")
    gc.at(8.3, g_perch[0] + 20, ry).pose(8.3, "sit")
    oc.pose(8.3, "sit").at(8.3, o_perch[0] - 30, ry, ease=HOP_UP)
    oc.at(8.65, o_perch[0] + 10, ry - 46, ease=HOP_DOWN).at(9.3, 372, 326).pose(9.3, "sit")
    gc.at(9.9, g_perch[0] + 20, ry).pose(9.9, "sleep")
    T = max(a.end() for a in (oc, gc, cl))
    marks, zc = zzz(k, g_perch[0] + 24, ry - 36, T)
    css = oc.css(T) + gc.css(T) + cl.css(T) + zc + jiggle(5.6, T)
    return oc.svg() + gc.svg() + cl.svg() + marks, css, T, \
        "an orange tabby guards the Last Year window; a fat gray cat climbs up on the second try, they fight, " \
        "the orange one gets thrown off and the gray one goes to sleep up there"


def truce(L, k, palette="bit"):
    oc, gc, cl = Act("oc", k, "orange", palette), Act("gc", k, "gray", palette), Act("cl", k, "cloud", palette)
    gc.at(0, -80, 326).walk(0.3, 3.0, -80, 110, 326).pose(3.0, "sit")
    oc.at(0, 500, 326).at(0.9, 500, 326).walk(0.9, 2.2, 500, 214, 326).pose(2.2, "sit")
    oc.at(3.2, 214, 326, True).pose(3.2, "paw").pose(3.45, "sit")
    gc.at(3.5, 110, 326).pose(3.5, "paw").pose(3.75, "sit")
    oc.pose(3.95, "paw").pose(4.15, "none").at(4.15, 214, 326, True)
    gc.pose(4.15, "none").at(4.15, 110, 326)
    mid = (126, 334)
    cl.at(0, *mid).pose(0, "none").at(4.1, *mid).pose(4.15, "fight")
    for i, dx in enumerate((-16, 18, -12, 20, -8, 10, 0)):
        cl.at(4.35 + i * .27, mid[0] + dx, mid[1] - (5 if i % 2 else 0))
    cl.pose(6.2, "none")
    gc.at(6.2, 104, 326).pose(6.2, "sit")
    oc.at(6.2, 226, 326, True).pose(6.2, "sit")
    gc.at(7.0, 104, 326).pose(7.0, "sleep")
    oc.walk(7.3, 7.9, 226, 172, 326).pose(7.9, "sit").at(8.4, 172, 326, True).pose(8.4, "sleep")
    T = max(a.end() for a in (oc, gc, cl))
    marks, zc = zzz(k, 150, 292, T)
    return gc.svg() + oc.svg() + cl.svg() + marks, oc.css(T) + gc.css(T) + cl.css(T) + zc, T, \
        "a fat gray cat and an orange tabby meet in the middle, swat at each other, brawl in a dust cloud, " \
        "then fall asleep side by side"


def zoomies(L, k, palette="bit"):
    ry, wy = L["ry"], 22
    oc, gc = Act("oc", k, "orange", palette), Act("gc", k, "gray", palette)
    tail = Act("tl", k, "tail", palette)
    gc.at(0, -80, 326).walk(0.2, 2.6, -80, 196, 326).pose(2.6, "sit")
    oc.at(0, 520, 326).pose(0, "run").at(1.0, 520, 326)
    oc.walk(1.0, 1.7, 520, -70, 326, "run")
    oc.at(1.71, -70, ry).walk(2.2, 3.0, -70, 500, ry, "run")
    oc.at(3.01, 500, wy).walk(3.3, 4.0, 500, -70, wy, "run")
    oc.at(4.01, -70, 326).walk(4.4, 5.15, -70, 176, 326, "run")
    gc.at(5.0, 196, 326, True).pose(5.0, "paw")
    gc.hop(5.1, 5.45, (196, 326), (168, 326), lift=30, flip=True).pose(5.45, "sit")
    oc.pose(5.4, "none")
    gc.at(6.2, 168, 326, True).pose(6.2, "sleep")
    tail.at(0, 146, 326, True).pose(0, "none").at(5.4, 146, 326, True).pose(5.5, "flick")
    T = max(a.end() for a in (oc, gc, tail))
    marks, zc = zzz(k, 196, 286, T)
    return oc.svg() + tail.svg() + gc.svg() + marks, oc.css(T) + gc.css(T) + tail.css(T) + zc, T, \
        "an orange tabby has the zoomies across every window until a fat gray cat sits on it; only its tail sticks out"


ACTS = {"nap": nap, "keyboard": keyboard, "chase": chase, "stairs": stairs, "mug": mug, "folder": folder,
        "brawl": brawl, "truce": truce, "zoomies": zoomies}
