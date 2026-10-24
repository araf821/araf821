"""Tiny raster kit for drawing pixel sprites from shapes, then outlining them."""
import math


def grid(w, h):
    return [["."] * w for _ in range(h)]


def ellipse(g, cx, cy, rx, ry, code):
    for y, row in enumerate(g):
        for x in range(len(row)):
            if ((x + .5 - cx) / rx) ** 2 + ((y + .5 - cy) / ry) ** 2 <= 1:
                row[x] = code


def tri(g, a, b, c, code):
    def side(p, q, r):
        return (p[0] - r[0]) * (q[1] - r[1]) - (q[0] - r[0]) * (p[1] - r[1])
    for y, row in enumerate(g):
        for x in range(len(row)):
            p = (x + .5, y + .5)
            d = (side(p, a, b), side(p, b, c), side(p, c, a))
            if not (min(d) < 0 < max(d)):
                row[x] = code


def box(g, x0, y0, x1, y1, code):
    for y in range(max(0, y0), min(len(g), y1)):
        for x in range(max(0, x0), min(len(g[0]), x1)):
            g[y][x] = code


def put(g, cells, code):
    for x, y in cells:
        if 0 <= y < len(g) and 0 <= x < len(g[0]):
            g[y][x] = code


def outline(g):
    h, w = len(g), len(g[0])
    edge = []
    for y in range(h):
        for x in range(w):
            if g[y][x] == ".":
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < w and 0 <= ny < h) or g[ny][nx] == ".":
                    edge.append((x, y))
                    break
    put(g, edge, "#")


def rows(g):
    return ["".join(r) for r in g]


def stripes(rows_, cells, code="s"):
    g = [list(r) for r in rows_]
    put(g, cells, code)
    return ["".join(r) for r in g]


# --- the fat gray cat ('g' fur, 'w' eye whites) -------------------------------------------
def overlay(base, top):
    """Composite an outlined layer over another so its contour shows where they overlap."""
    for y, row in enumerate(top):
        for x, c in enumerate(row):
            if c != ".":
                base[y][x] = c
    return base


def fat_sit(paw=False):
    body = grid(23, 17)
    ellipse(body, 11.5, 12.4, 10.8, 4.8, "g")
    if paw:
        box(body, 20, 8, 23, 12, "g")
    outline(body)
    head = grid(23, 17)
    ellipse(head, 11.5, 6.4, 6.6, 4.9, "g")
    tri(head, (5.0, 0), (4.6, 4.8), (9.0, 2.4), "g")
    tri(head, (18.0, 0), (18.4, 4.8), (14.0, 2.4), "g")
    outline(head)
    g = overlay(body, head)
    put(g, [(8, 5), (9, 5), (13, 5), (14, 5), (8, 6), (14, 6)], "e")
    put(g, [(9, 6), (13, 6)], "#")
    put(g, [(11, 8)], "n")
    return rows(g)


def fat_walk(frame):
    body = grid(24, 14)
    ellipse(body, 10.4, 8.0, 9.2, 4.6, "g")
    tri(body, (0, 2.0), (1.4, 7.6), (3.6, 6.0), "g")
    legs = [(3, 5), (7, 9), (12, 14), (16, 18)] if frame == 0 else [(5, 7), (13, 15)]
    for x0, x1 in legs:
        box(body, x0, 11, x1, 14, "g")
    outline(body)
    head = grid(24, 14)
    ellipse(head, 19.0, 4.6, 4.2, 3.6, "g")
    tri(head, (15.6, 0), (15.8, 3.4), (18.6, 1.8), "g")
    tri(head, (22.8, 0), (19.6, 1.8), (23.4, 3.6), "g")
    outline(head)
    g = overlay(body, head)
    put(g, [(19, 4)], "e")
    put(g, [(20, 4)], "#")
    put(g, [(22, 6)], "n")
    return rows(g)


def fat_sleep(frame):
    body = grid(24, 11)
    ellipse(body, 13.4, 6.8 - .3 * frame, 10.2, 3.9 + .4 * frame, "g")
    outline(body)
    put(body, [(x, 9) for x in range(9, 17)], "#")
    head = grid(24, 11)
    ellipse(head, 5.2, 6.6, 4.6, 3.6, "g")
    tri(head, (1.4, 1.2), (2.0, 4.6), (4.8, 3.4), "g")
    tri(head, (6.2, 1.0), (5.2, 3.8), (8.2, 3.8), "g")
    outline(head)
    g = overlay(body, head)
    put(g, [(3, 7), (4, 7)], "#")
    return rows(g)


# --- the orange tabby ('q' fur, 's' stripes), from the original desk cat --------------------
def tabby(rows_, cells, extra=()):
    g = stripes([r.replace("o", "q") for r in rows_], cells)
    for code, pts in extra:
        g = stripes(g, pts, code)
    return g


# --- the fight: a wobbling dust cloud with gray and orange limbs poking out ------------------
def cloud(phase):
    W, H, cx, cy = 32, 22, 16, 11.5
    g = grid(W, H)
    for y in range(H):
        for x in range(W):
            dx, dy = (x + .5 - cx) / 12.0, (y + .5 - cy) / 7.6
            a, r = math.atan2(dy, dx), math.hypot(dx, dy)
            if r <= .8 + .14 * abs(math.sin(4.5 * a + phase)):
                g[y][x] = "o"
    limbs = [(phase * .8 + .4, "g"), (phase * .8 + 2.1, "q"), (phase * .8 + 3.6, "g"), (phase * .8 + 5.1, "q")]
    for a, code in limbs:
        for i in range(5):
            x = int(cx + math.cos(a) * (9.4 + i * 1.2))
            y = int(cy + math.sin(a) * (6.0 + i * .9))
            c = "s" if code == "q" and i % 2 else code
            put(g, [(x + dx_, y + dy_) for dx_ in (0, 1, 2) for dy_ in (0, 1)], c)
    for ring, span in ((.42, 2.6), (.22, 2.0)):
        for i in range(40):
            a = phase * 1.4 + ring * 7 + span * i / 40
            x, y = int(cx + math.cos(a) * ring * 12), int(cy + math.sin(a) * ring * 7.6)
            if g[y][x] == "o":
                g[y][x] = "#"
    outline(g)
    spots = [(0, 1), (26, 0), (1, 16), (27, 15)]
    for k in range(2):
        sx, sy = spots[(int(phase * 10) + k * 2) % 4]
        put(g, [(sx + i, sy + j) for j, r in enumerate(STAR) for i, c in enumerate(r) if c == "#"], "#")
    return rows(g)


STAR = ["..#..", "#.#.#", ".###.", "#.#.#", "..#.."]
TAIL = [["..###..", ".#qsq#.", "#q#.#s#", "##..#q#", "....#s#", "....#q#", "...#sq#", "...###."],
        [".###...", "#qsq#..", "#s#.#q#", "#q#..##", "#s#....", "#q#....", "#qs#...", ".###..."]]
