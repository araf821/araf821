"""Vector cats for the contributions plate, drawn from Araf's two cats.

The ginger: soft ginger tabby, gentle darker stripes, cream muzzle and brows, a small white spot on the chest,
hazel-gold eyes, pink nose, tall ears. The gray: solid blue-gray, chubby cheeks, round gold eyes, dark nose.

Every pose is drawn in its own unit space with the ground at y=0. Side poses face right.
Each function returns (svg, css) with class names prefixed by `k` so poses can share a page.
"""
from math import hypot

# ginger
FUR, FUR_LIT, STRIPE, FAR = "#dc8b4f", "#e9a56b", "#ac5f30", "#bb703f"
CREAM, WHITE, NOSE, EAR_IN = "#f2d8bb", "#f8efe4", "#e59d98", "#e8a9a3"
EYE, EYE_RIM, PUPIL = "#cdb556", "#6e4a1e", "#111111"
# gray
GRAY, GRAY_DK, GRAY_LT, GRAY_MZ = "#5c5f67", "#46484f", "#6e7179", "#73767e"
GRAY_EAR, GRAY_NOSE, GOLD, GOLD_RIM, LID, WHISK = "#6f6468", "#2c2e33", "#e8a72c", "#a86a14", "#25272c", "#a3a7ae"


def _n(v):
    """A coordinate rounded to one decimal, to keep paths short."""
    return f"{round(v, 1):g}"


def _path(pts, closed=True):
    """A smooth curve through pts; an optional third value per point scales its tangent (0 makes a corner)."""
    P = [(p[0], p[1], p[2] if len(p) > 2 else 1) for p in pts]
    n = len(P)
    at = (lambda i: P[i % n]) if closed else (lambda i: P[min(max(i, 0), n - 1)])
    d = f"M{_n(P[0][0])},{_n(P[0][1])}"
    for i in range(n if closed else n - 1):
        a, b, c, e = at(i - 1), at(i), at(i + 1), at(i + 2)
        d += (f"C{_n(b[0] + (c[0] - a[0]) / 6 * b[2])},{_n(b[1] + (c[1] - a[1]) / 6 * b[2])} "
              f"{_n(c[0] - (e[0] - b[0]) / 6 * c[2])},{_n(c[1] - (e[1] - b[1]) / 6 * c[2])} {_n(c[0])},{_n(c[1])}")
    return d + ("Z" if closed else "")


def _tube(pts, w0, w1):
    """Outline of a limb or tail along the centreline pts, tapering from width w0 to w1, round at the far end."""
    n, L, R = len(pts), [], []
    for i, (x, y) in enumerate(pts):
        (ax, ay), (bx, by) = pts[max(i - 1, 0)], pts[min(i + 1, n - 1)]
        m = hypot(bx - ax, by - ay)
        tx, ty, w = (bx - ax) / m, (by - ay) / m, (w0 + (w1 - w0) * i / (n - 1)) / 2
        L.append((x - ty * w, y + tx * w))
        R.append((x + ty * w, y - tx * w))
    tip = (pts[-1][0] + tx * w, pts[-1][1] + ty * w)
    return _path([(*L[0], 0)] + L[1:] + [tip] + R[:0:-1] + [(*R[0], 0)])


def _pivot(x, y, inner, cls=""):
    """A group whose own origin sits at (x, y), so CSS rotations turn around that joint."""
    c = f' class="{cls}"' if cls else ""
    return f'<g transform="translate({x:g},{y:g})"><g{c}>{inner}</g></g>'


def _around(x, y, inner, cls):
    """Rotate already-placed shapes around (x, y)."""
    return _pivot(x, y, f'<g transform="translate({-x:g},{-y:g})">{inner}</g>', cls)


def _sample(keys, f):
    """Value at fraction f of a loop passing smoothly through (fraction, value) keys; values may be tuples."""
    keys = sorted(keys)
    m = len(keys)
    i = max([j for j in range(m) if keys[j][0] <= f] or [-1])
    (f0, b), (f1, c) = keys[i % m], keys[(i + 1) % m]
    a, d = keys[(i - 1) % m][1], keys[(i + 2) % m][1]
    u = ((f - f0) % 1) / (((f1 - f0) % 1) or 1)
    one = lambda a, b, c, d: .5 * (2 * b + (c - a) * u + (2 * a - 5 * b + 4 * c - d) * u * u + (3 * b - a - 3 * c + d) * u ** 3)
    return tuple(map(one, a, b, c, d)) if isinstance(b, tuple) else one(a, b, c, d)


def _cycle(name, keys, n=12):
    """Keyframes sampled from a smooth loop through (fraction, angle) or (fraction, (dy, angle)) keys,
    so linear timing between them stays fluid."""
    def frame(v):
        dy, a = v if isinstance(v, tuple) else (0, v)
        return (f"translate(0,{dy:.2f}px) " if isinstance(v, tuple) else "") + f"rotate({a:.1f}deg)"
    return f"@keyframes {name}{{{''.join(f'{s / n * 100:.4g}%{{transform:{frame(_sample(keys, s / n))}}}' for s in range(n + 1))}}}"


def _clip(cid, d):
    return f'<clipPath id="{cid}"><path d="{d}"/></clipPath>'


def _stripe(x, y, length, w, lean=-2.4):
    """A tabby stripe hanging from (x, y), tapering to a point."""
    d = _path([(x - w / 2, y, 0), (x + w / 2, y, 0), (x + w * .3 + lean * .6, y + length * .6), (x + lean, y + length, 0),
               (x - w * .4 + lean * .5, y + length * .55)])
    return f'<path d="{d}"/>'


def _ear(base_a, tip, base_b, fill, inner=None, inner_fill=EAR_IN):
    """A rounded triangular ear; `inner` is its pink lining."""
    out = (f'<path d="M{base_a[0]:g},{base_a[1]:g} L{tip[0]:g},{tip[1]:g} L{base_b[0]:g},{base_b[1]:g} Z" fill="{fill}" '
           f'stroke="{fill}" stroke-width="2.6" stroke-linejoin="round"/>')
    if inner:
        (a, t, b) = inner
        out += (f'<path d="M{a[0]:g},{a[1]:g} Q{(a[0] + b[0]) / 2:g},{(a[1] + b[1]) / 2 - 1:g} {b[0]:g},{b[1]:g} L{t[0]:g},{t[1]:g} Z" '
                f'fill="{inner_fill}" stroke="{inner_fill}" stroke-width=".8" stroke-linejoin="round"/>')
    return out


def _eye(cid, rx, ry, px, py, s, shift=0):
    """A hazel-gold ginger eye with a soft upper lid; s is 1 for the right eye, -1 for the left."""
    edge = f"M{rx + 1:g},{-ry * .5 + s * .3:.2f}Q{shift:g},{-ry * .8:.2f} {-rx - 1:g},{-ry * .5 - s * .3:.2f}"
    return (f'<defs><clipPath id="{cid}"><ellipse rx="{rx:g}" ry="{ry:g}"/></clipPath></defs>'
            f'<ellipse rx="{rx:g}" ry="{ry:g}" fill="{EYE}"/>'
            f'<ellipse cx="{shift:g}" rx="{px:g}" ry="{py:g}" fill="{PUPIL}"/>'
            f'<circle cx="{shift - px * .45:.2f}" cy="{-ry * .2:.2f}" r="{ry * .24:.2f}" fill="#fff"/>'
            f'<g clip-path="url(#{cid})"><path d="{edge}V{-ry - 1:g}H{rx + 1:g}Z" fill="{FUR}"/>'
            f'<path d="{edge}" fill="none" stroke="{EYE_RIM}" stroke-width=".7"/></g>'
            f'<ellipse rx="{rx:g}" ry="{ry:g}" fill="none" stroke="{EYE_RIM}" stroke-width=".55"/>')


def _rings(cid, pts, w0, w1, colour, dash):
    """A tapered tube with tabby rings, clipped to its own outline."""
    d = _tube(pts, w0, w1)
    line = _path(pts, closed=False)
    return (f'<defs>{_clip(cid, d)}</defs><path d="{d}" fill="{FUR}"/>'
            f'<path d="{line}" clip-path="url(#{cid})" fill="none" stroke="{colour}" stroke-width="{w0 + 4:g}" stroke-dasharray="{dash}"/>')


# ---- a knitted scarf for the cold months ------------------------------------------------------
def _knit(color, d):
    return (f'<path d="{d}" fill="{color}"/>'
            f'<path d="{d}" fill="none" stroke="#000" stroke-opacity=".18" stroke-width=".7" stroke-dasharray=".8 1.6"/>')


def _fringe(color, a, b, d, n=4):
    """Short tassels along the edge a-b, each pointing along d."""
    return "".join(f'<path d="M{a[0] + (b[0] - a[0]) * i / (n - 1):.1f},{a[1] + (b[1] - a[1]) * i / (n - 1):.1f} '
                   f'l{d[0]:.1f},{d[1]:.1f}" stroke="{color}" stroke-width="1.1" stroke-linecap="round"/>' for i in range(n))


def _paint(scarf, k):
    """A scarf is one colour, or (base, stripe) for a striped knit. Returns (defs, fill, base colour)."""
    if isinstance(scarf, str):
        return "", scarf, scarf
    base, stripe = scarf
    pat = (f'<pattern id="{k}knit" width="5" height="5" patternUnits="userSpaceOnUse" patternTransform="rotate(-35)">'
           f'<rect width="5" height="5" fill="{base}"/><rect width="2.4" height="5" fill="{stripe}"/></pattern>')
    return f"<defs>{pat}</defs>", f"url(#{k}knit)", base


def _side_scarf(scarf, k, flowing):
    defs, paint, base = _paint(scarf, k)
    band = _knit(paint, "M14.4,-42.6 C20,-42.8 25.6,-40.6 29.2,-36.8 L29.8,-30.8 C26,-34.4 21,-36.8 15.6,-36.8 Z")
    if flowing:
        tail = _pivot(17, -40, _knit(paint, "M0,0 C-6,-2.4 -12,-1 -19,-4.6 L-17.6,1 C-11,3 -5,3.4 0,4.6 Z")
                      + _fringe(base, (-18.8, -3.8), (-17.8, .4), (-2.6, .4), 3), f"{k}scarf")
    else:
        tail = _pivot(25.6, -34.6, _knit(paint, "M0,0 L4.6,.4 L3.6,12.6 L-.8,12 Z") + _fringe(base, (-.4, 12.2), (3.4, 12.6), (0, 2.6)))
    return defs + tail + band


HAT_TRIM = "#f6f1ea"


def _side_hat(color):
    """A floppy knit hat on the side-view head, covering the ears, its tip trailing back to a pom-pom."""
    return (f'<path d="M-2,-13 L16.4,-16.6 C15.4,-23.4 9,-29.4 -1.6,-30 C-6,-30.2 -9.6,-28.6 -11.6,-25.8 '
            f'C-6.6,-26 -3.8,-22.4 -2,-13 Z" fill="{color}"/>'
            f'<path d="M2.4,-24.6 C6,-23.8 9.4,-21.4 11.6,-17.6" stroke="#000" stroke-opacity=".14" stroke-width="2" fill="none" stroke-linecap="round"/>'
            f'<path d="M-2.8,-11.6 L17.4,-15.4 L16.6,-19.2 L-3.6,-15.4 Z" fill="{HAT_TRIM}" stroke="{HAT_TRIM}" stroke-width="2" stroke-linejoin="round"/>'
            f'<circle cx="-11.8" cy="-25.6" r="3.3" fill="{HAT_TRIM}"/>')


def _front_hat(color):
    """The same hat seen from the front, sitting between the ears and leaning off to one side."""
    return (f'<path d="M-10.6,-64 C-8.6,-75 1,-84 15,-82.6 C10.4,-79 8.6,-72.6 9.6,-64 Z" fill="{color}"/>'
            f'<path d="M-2,-65 C1,-72.4 6,-78 12,-80.6" stroke="#000" stroke-opacity=".14" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
            f'<rect x="-12.6" y="-67.4" width="24.6" height="6.6" rx="3.3" fill="{HAT_TRIM}"/>'
            f'<circle cx="15.4" cy="-82.4" r="4" fill="{HAT_TRIM}"/>')


# ---- the ginger, side view ---------------------------------------------------------------------
# Joints in body space: neck N, spine hinge M, shoulders S, hips H, tail root T. Far limbs sit a little back and up.
N, M, T, HEAD = (21.4, -41.6), (-4, -29), (-27, -36), 1.2
S_NEAR, S_FAR, H_NEAR, H_FAR, FAR_UP = (18.6, -27), (13.6, -27.6), (-17.4, -28), (-13.6, -28.6), -1.2
TORSO = [(13, -39.6), (2, -38.2), (-9, -38.6), (-18, -40.4), (-24.6, -38.6), (-28.4, -33.4), (-29.4, -26.4), (-26.4, -21),
         (-18, -21.2), (-6, -19.6), (8, -17.8), (16.6, -18), (23.4, -21.6), (27.4, -27.6), (28.6, -34), (27.6, -40.6), (23.4, -46),
         (17, -45)]


def _side_torso(k, half=""):
    """Neck to rump in one outline; `half` ("f" or "r") keeps only the front or rear, so the spine can bend between them."""
    d, cid = _path(TORSO), f"{k}t{half}"
    marks = (f'<ellipse cx="4" cy="-15.6" rx="27" ry="7" fill="{FUR_LIT}" opacity=".6"/>'
             f'<path d="{_path([(25.4, -34.6), (27.2, -32), (26.6, -29.2), (24.8, -30.8)])}" fill="{WHITE}"/>'
             f'<g fill="{STRIPE}" opacity=".6">'
             + "".join(_stripe(x, -42, n, w, -2.2) for x, n, w in ((10.4, 11, 2.8), (4, 13.4, 3.4), (-2.6, 12, 3), (-9.4, 13.6, 3.4), (-16.4, 11.4, 3)))
             + "</g>")
    body = f'<defs>{_clip(cid, d)}</defs><path d="{d}" fill="{FUR}"/><g clip-path="url(#{cid})">{marks}</g>'
    if not half:
        return body
    keep = "M-6,-80H60V20H-6Z" if half == "f" else "M-60,-80H-2V20H-60Z"
    return f'<defs>{_clip(cid + "x", keep)}</defs><g clip-path="url(#{cid}x)">{body}</g>'


def _front_leg(fill, ringed, cls=("", "")):
    """Shoulder to wrist, then the paw on its own joint; cls names the CSS classes of the two joints."""
    rings = (f'<path d="M-3.6,12 h4.4 M-3.2,16.8 h4" stroke="{STRIPE}" stroke-width="1.7" stroke-linecap="round" opacity=".8"/>'
             if ringed else "")
    paw = (f'<path d="{_tube([(0, -2), (.6, 2.4)], 5.4, 4.8)}" fill="{fill}"/>'
           f'<ellipse cx="1.6" cy="3.4" rx="4.6" ry="2.6" fill="{fill}"/>')
    upper = f'<path d="{_tube([(0, -5), (.3, 8), (.4, 21)], 9, 5.6)}" fill="{fill}"/>{rings}'
    return _pivot(0, 0, upper + _pivot(.4, 21, paw, cls[1]), cls[0])


def _hind_leg(fill, ringed, cls=("", "", "")):
    """Haunch from the hip to the knee, the shin back to the hock, then the foot: the cat's zig-zag hind leg."""
    thigh = (f'<path d="{_path([(-9.6, -5), (-1.4, -10), (7, -7.4), (9.6, 1), (7.4, 9.4), (3.4, 14.4), (-2.4, 12.4), (-8.4, 6), (-10.6, 0)])}" '
             f'fill="{fill}"/>')
    shin = f'<path d="{_tube([(.6, -1.6), (-4.2, 3), (-8.8, 7)], 8.2, 5.6)}" fill="{fill}"/>'
    foot = (f'<path d="{_tube([(0, -1.4), (1, 3), (1.8, 6)], 5.6, 4.6)}" fill="{fill}"/>'
            f'<ellipse cx="3" cy="6" rx="4.6" ry="2.6" fill="{fill}"/>')
    if ringed:
        thigh += (f'<g fill="none" stroke="{STRIPE}" stroke-width="1.8" stroke-linecap="round" opacity=".75">'
                  '<path d="M-9.6,.6 Q-4.4,-1.6 .6,1.6"/><path d="M-8.6,5.8 Q-4,3.8 .6,6.8"/></g>')
        shin += f'<path d="M-2,-.4 l-1.6,4 M-5.6,2.6 l-1.2,3.4" stroke="{STRIPE}" stroke-width="1.6" stroke-linecap="round" opacity=".8"/>'
    return _pivot(0, 0, thigh + _pivot(3, 12.4, shin + _pivot(-8.8, 7, foot, cls[2]), cls[1]), cls[0])


def _side_head(k, hat=None):
    sil = _path([(-4.4, -6), (-1.6, -13), (6, -16.8), (13.4, -15), (18.4, -11), (21.2, -7.6, .8), (24.2, -4.6, .5),
                 (23.8, -1.6), (21.6, .8), (17.6, 2.8), (11, 4.8), (3, 5.2), (-3, 2)])
    muzzle = _path([(15.8, -3.2), (20, -5), (23.6, -3.4), (23.2, -.6), (20.6, 1.4), (16.4, 3), (12.8, 2), (13, -.8)])
    return (f'<g transform="scale({HEAD})"><defs>{_clip(k + "h", sil)}</defs>'
            + _ear((9, -15.4), (13.4, -25.4), (16.8, -12.4), FAR)
            + f'<path d="{sil}" fill="{FUR}"/>'
            + _ear((-.4, -13.4), (4.4, -27.2), (10.8, -16.4), FUR, ((3.4, -16.4), (5, -24.2), (8.8, -16.8)))
            + f'<g clip-path="url(#{k}h)">'
              f'<ellipse cx="13.6" cy="-11.2" rx="4.2" ry="1.8" fill="{FUR_LIT}"/>'
              f'<path d="{muzzle}" fill="{CREAM}"/>'
              f'<g stroke="{STRIPE}" stroke-width="1.5" stroke-linecap="round" fill="none" opacity=".85">'
              '<path d="M3.4,-15.6 q.8,2.4 1.6,4.6"/><path d="M7.2,-16.8 q.4,2.6 .9,4.8"/><path d="M10.6,-16.4 q0,2.4 .2,4.4"/>'
              '<path d="M11.4,-4.6 q-3.6,-.6 -7,.2"/><path d="M11.6,-1.8 q-3.4,.2 -6.4,1.6"/></g></g>'
            + _pivot(15.2, -6.8, _eye(k + "e", 2.9, 3.4, 1.7, 2.8, 1, .6))
            + f'<path d="M21.6,-5.6 L24.4,-5 L23.2,-3 Z" fill="{NOSE}" stroke="{NOSE}" stroke-width="1" stroke-linejoin="round"/>'
            + f'<path d="M22.8,-1 q-1.4,1.6 -3.6,1.2" stroke="{FAR}" stroke-width=".7" fill="none" stroke-linecap="round"/>'
            + f'<g stroke="{WHITE}" stroke-width=".5" stroke-linecap="round" opacity=".75">'
              '<path d="M20.4,-2.4 L31.6,-5.4"/><path d="M20.6,-1 L31.6,0"/><path d="M20,.4 L29.6,3.2"/></g>'
            + (_side_hat(hat) if hat else "") + "</g>")


def _side_tail(k, pts):
    return _rings(k + "tl", pts, 7, 5, STRIPE, "2.4 4.4")


RUN_TAIL = [(0, 0), (-9, -1.6), (-17.6, -6), (-24.4, -12.6)]
STAND_TAIL = [(0, 0), (-7, -5), (-9.6, -16), (-6, -26.6), (0, -30.6), (3.4, -28)]
# A gallop in fractions of the stride: hinds land at 0 and push off into the stretched leap, fronts land at .46,
# then the back arches and all four feet gather under the belly. Far legs follow their near pair a beat later.
GALLOP = {
    "f1": [(0, 10), (.15, -30), (.3, -62), (.4, -66), (.46, -40), (.56, 0), (.66, 28), (.76, 35)],
    "f2": [(0, 100), (.15, 70), (.3, 10), (.4, -4), (.46, 25), (.56, 0), (.66, 12), (.76, 80)],
    "h1": [(0, -31.4), (.11, -1.4), (.22, 43.6), (.34, 53.6), (.55, 23.6), (.86, -36.4)],
    "h2": [(0, 14.9), (.11, 4.9), (.22, -35.1), (.34, -35.1), (.55, 19.9), (.86, 24.9)],
    "h3": [(0, 28.5), (.11, 3.5), (.22, 58.5), (.34, 78.5), (.55, -6.5), (.86, 3.5)],
    "sf": [(0, 6), (.2, -3), (.38, -10), (.6, 2), (.86, 14)],
    "tl": [(0, 6), (.4, -4), (.62, -8), (.86, 2)],
    "hm": [(0, 4), (.42, 7), (.56, 3), (.86, -4)],
    "bb": [(0, (-1, -4)), (.11, (-1.2, -3)), (.22, (-.6, -1)), (.38, (-3.4, 0)), (.5, (.4, 2.5)), (.6, (-1.2, 2)), (.7, (-.8, 1)),
           (.86, (-4.6, -1))],
}


def _gait_css(k, period, gait, lag, extra=()):
    """One timing rule for every joint, its keyframes, and the far legs running `lag` of a stride behind."""
    joints = [(f"{limb}{side}{j}", f"{limb}{j}", side == "f") for limb, n in (("f", 2), ("h", 3)) for side in "nf" for j in range(1, n + 1)]
    named = [(c, name) for c, name, _ in joints] + [(c, c) for c in extra]
    return ([",".join(f".{k}{c}" for c, _ in named) + f"{{animation:{period}s linear infinite}}",
             "".join(f".{k}{c}{{animation-name:{k}{name}" + (f";animation-delay:-{period * lag:.3f}s" if far else "") + "}"
                     for c, name, far in joints),
             "".join(f".{k}{c}{{animation-name:{k}{c}}}" for c in extra)]
            + [_cycle(f"{k}{name}", keys) for name, keys in gait.items()])


def tabby_run(k="tr", period=.3, scarf=None, hat=None):
    """Side view at a gallop: hinds land and push into a stretched leap, fronts land, the back arches to gather."""
    front = lambda inner: _around(*M, inner, f"{k}sf")
    rear = lambda inner: _around(*M, inner, f"{k}sr")
    far = (rear(_pivot(*H_FAR, _hind_leg(FAR, False, (f"{k}hf1", f"{k}hf2", f"{k}hf3"))))
           + front(_pivot(*S_FAR, _front_leg(FAR, False, (f"{k}ff1", f"{k}ff2")))))
    near = (rear(_pivot(*H_NEAR, _hind_leg(FUR, True, (f"{k}hn1", f"{k}hn2", f"{k}hn3"))))
            + front(_pivot(*S_NEAR, _front_leg(FUR, True, (f"{k}fn1", f"{k}fn2")))))
    tail = rear(_pivot(*T, _side_tail(k, RUN_TAIL), f"{k}tl"))
    wrap = front(_side_scarf(scarf, k, True)) if scarf else ""
    head = front(_pivot(*N, _side_head(k, hat), f"{k}hm"))
    svg = (f'<g class="{k}bb"><g transform="translate(0,{FAR_UP})">{far}</g>{tail}{rear(_side_torso(k, "r"))}'
           f'{front(_side_torso(k, "f"))}{near}{wrap}{head}</g>')
    gait = {**GALLOP, "sr": [(f, -a) for f, a in GALLOP["sf"]]}
    css = _gait_css(k, period, gait, .1, ("sf", "sr", "tl", "hm", "bb")) + [
        f".{k}scarf{{animation:{k}flap {period * 1.5:.2f}s ease-in-out infinite}}"
        f"@keyframes {k}flap{{0%,100%{{transform:rotate(-6deg) scale(1,1)}}50%{{transform:rotate(7deg) scale(.94,1.12)}}}}"]
    return svg, css


def tabby_stand(k="ts", look_at=None, look_back=.18, scarf=None, hat=None):
    """Side view standing; at `look_at` seconds the head turns back over the shoulder."""
    far = f'<g transform="translate(0,{FAR_UP})">{_pivot(*H_FAR, _hind_leg(FAR, False))}{_pivot(*S_FAR, _front_leg(FAR, False))}</g>'
    near = _pivot(*H_NEAR, _hind_leg(FUR, True)) + _pivot(*S_NEAR, _front_leg(FUR, True))
    tail = _pivot(*T, _side_tail(k, STAND_TAIL))
    head = _pivot(*N, _side_head(k, hat), f"{k}head")
    wrap = _side_scarf(scarf, k, False) if scarf else ""
    svg = f"{far}{tail}{_side_torso(k)}{near}{wrap}{head}"
    css = []
    if look_at is not None:
        css.append(f".{k}head{{animation:{k}look {look_back}s cubic-bezier(.3,0,.2,1) {look_at:.2f}s both}}"
                   f"@keyframes {k}look{{from{{transform:none}}to{{transform:translate(-3px,-2px) scale(-1,1)}}}}")
    return svg, css


# ---- the ginger, sitting and facing us -----------------------------------------------------------
def _mirror(half):
    """A symmetric outline from its right half, listed top to bottom."""
    return half + [(-x, y, *r) for x, y, *r in reversed(half) if x]


def tabby_front(k="tf", blink_every=4.2, delay=0, scarf=None, hat=None):
    """Facing us, sitting, tail up its side; blinks now and then."""
    torso = _path(_mirror([(0, -42), (9.6, -41), (14.4, -36.4), (16.6, -27.6), (17.6, -17), (15, -5.6), (8, -.6), (0, 0)]))
    head_d = _path(_mirror([(0, -66.6), (8.2, -65.6), (13.8, -61.8), (16.6, -55), (16.8, -48.6), (14.6, -43.2), (10, -39.4),
                            (4.6, -37.8), (0, -37.4)]))
    clip = _clip(k + "b", torso) + _clip(k + "h", head_d)
    body = (f'<path d="{torso}" fill="{FUR}"/><g clip-path="url(#{k}b)">'
            f'<ellipse cx="0" cy="-30" rx="9" ry="12" fill="{FUR_LIT}" opacity=".75"/>'
            f'<g stroke="{STRIPE}" stroke-width="2.4" stroke-linecap="round" fill="none" opacity=".8">'
            '<path d="M-17.6,-31 Q-13.6,-30 -11.6,-26"/><path d="M17.6,-31 Q13.6,-30 11.6,-26"/>'
            '<path d="M-18,-24 Q-14.4,-23 -12.6,-19"/><path d="M18,-24 Q14.4,-23 12.6,-19"/>'
            '<path d="M-9,-38.6 Q0,-34.6 9,-38.6"/></g>'
            f'<path d="{_path([(0, -34, 0), (1.6, -30.4), (0, -27.4, 0), (-1.6, -30.4)])}" fill="{WHITE}"/></g>')
    haunches = "".join(
        f'<ellipse cx="{sx * 14.4}" cy="-10.6" rx="8.6" ry="10.4" fill="{FUR}"/>'
        f'<path d="M{sx * 22.4},-15.4 Q{sx * 16.6},-14.6 {sx * 13.6},-9" stroke="{STRIPE}" stroke-width="2.3" fill="none" stroke-linecap="round" opacity=".8"/>'
        f'<path d="M{sx * 23},-9.6 Q{sx * 18.6},-8.8 {sx * 16.6},-4.6" stroke="{STRIPE}" stroke-width="2.1" fill="none" stroke-linecap="round" opacity=".8"/>'
        f'<ellipse cx="{sx * 18.4}" cy="-2.7" rx="5.2" ry="2.9" fill="{FUR}"/>'
        f'<path d="M{sx * 14.8},-1.2 Q{sx * 18.4},.4 {sx * 22},-1.2" stroke="{FAR}" stroke-width=".9" fill="none" stroke-linecap="round"/>'
        for sx in (-1, 1))
    gap = f'<path d="M0,-17 L1.8,-4 L-1.8,-4 Z" fill="{FAR}" stroke="{FAR}" stroke-linejoin="round"/>'
    legs = "".join(
        f'<path d="{_tube([(x, -27), (x - sx * .2, -14), (x - sx * .3, -4)], 8, 6)}" fill="{FUR_LIT}"/>'
        f'<path d="M{x + sx * 3.9},-16 h{-sx * 3} M{x + sx * 3.7},-11 h{-sx * 2.6}" stroke="{STRIPE}" stroke-width="1.5" stroke-linecap="round" opacity=".85"/>'
        f'<ellipse cx="{x}" cy="-3.2" rx="5.3" ry="3.3" fill="{FUR_LIT}"/>'
        f'<path d="M{x - 1.5},-.9 v-1.7 M{x + 1.5},-.9 v-1.7" stroke="{FAR}" stroke-width=".85" stroke-linecap="round"/>'
        for x, sx in ((-5.6, -1), (5.6, 1)))
    tail = _pivot(14, -6, _rings(k + "tl", [(0, 0), (8, .6), (14, -4), (15.6, -13), (16.2, -20), (19.4, -25.4), (23, -25)],
                                 6, 4.4, STRIPE, "2.2 4"), f"{k}tail")
    ears = "".join(_ear((s * 16.4, -56.4), (s * 15.2, -79), (s * 5.4, -65), FUR,
                        ((s * 14.4, -59.6), (s * 14, -74.6), (s * 8.4, -64)))
                   for s in (-1, 1))
    eyes = "".join(_pivot(s * 7.4, -52.6, _eye(f"{k}e{s + 1}", 4.1, 4.2, 2.3, 3.5, s), f"{k}eye") for s in (-1, 1))
    head = (ears
            + f'<path d="{head_d}" fill="{FUR}"/>'
            + f'<g clip-path="url(#{k}h)">'
              f'<ellipse cx="-7.4" cy="-58.4" rx="4.6" ry="2.2" fill="{FUR_LIT}"/><ellipse cx="7.4" cy="-58.4" rx="4.6" ry="2.2" fill="{FUR_LIT}"/>'
              f'<path d="M0,-63 L0,-48.6" stroke="{FUR_LIT}" stroke-width="3.4" stroke-linecap="round"/>'
              f'<g stroke="{STRIPE}" stroke-width="1.6" stroke-linecap="round" fill="none" opacity=".9">'
              '<path d="M-2.6,-66 q.2,3.4 .5,6"/><path d="M2.6,-66 q-.2,3.4 -.5,6"/><path d="M-6.6,-64.8 q.8,2.6 1.6,4.4"/>'
              '<path d="M6.6,-64.8 q-.8,2.6 -1.6,4.4"/>'
              '<path d="M-11.8,-51 L-16.8,-51.6"/><path d="M11.8,-51 L16.8,-51.6"/>'
              '<path d="M-12.6,-46.8 L-17,-46"/><path d="M12.6,-46.8 L17,-46"/></g>'
              f'<ellipse cx="-3.5" cy="-44.4" rx="4.4" ry="3.4" fill="{CREAM}"/><ellipse cx="3.5" cy="-44.4" rx="4.4" ry="3.4" fill="{CREAM}"/>'
              f'<ellipse cx="0" cy="-40.6" rx="3.8" ry="2.6" fill="{CREAM}"/></g>'
            + eyes
            + f'<path d="M-2.3,-47.8 L2.3,-47.8 L0,-45.2 Z" fill="{NOSE}" stroke="{NOSE}" stroke-width="1.2" stroke-linejoin="round"/>'
            + f'<path d="M0,-45.2 v1.2 M0,-44 q-1.5,1.5 -2.8,.4 M0,-44 q1.5,1.5 2.8,.4" stroke="{FAR}" stroke-width=".75" '
              'fill="none" stroke-linecap="round"/>'
            + f'<g stroke="{WHITE}" stroke-width=".55" stroke-linecap="round" opacity=".75">'
              '<path d="M-7,-44.6 L-21,-47.2"/><path d="M-7,-43.2 L-21,-42.8"/><path d="M-7,-42 L-19.6,-38.8"/>'
              '<path d="M7,-44.6 L21,-47.2"/><path d="M7,-43.2 L21,-42.8"/><path d="M7,-42 L19.6,-38.8"/></g>')
    wrap = ""
    if scarf:
        defs, paint, colour = _paint(scarf, k)
        wrap = (defs + _knit(paint, "M6,-34.6 L11.6,-35.6 L12.8,-21 L7,-20.2 Z") + _fringe(colour, (7.4, -20.6), (12.4, -21), (0, 2.6))
                + _knit(paint, "M-14.6,-41 Q0,-34 14.6,-41 L15,-35.2 Q0,-28 -15,-35.2 Z"))
    topper = _front_hat(hat) if hat else ""
    svg = f"<defs>{clip}</defs>{tail}{body}{haunches}{gap}{legs}{wrap}{head}{topper}"
    T = blink_every
    css = [f".{k}eye{{animation:{k}blink {T}s {delay + 1.2:.2f}s infinite}}"
           f"@keyframes {k}blink{{0%,92%,100%{{transform:none}}95%{{transform:scale(1,.12)}}}}",
           f".{k}tail{{animation:{k}flick 3.4s ease-in-out {delay + .6:.2f}s infinite}}"
           f"@keyframes {k}flick{{0%,70%,100%{{transform:none}}80%{{transform:rotate(-7deg)}}90%{{transform:rotate(3deg)}}}}"]
    return svg, css


# ---- the gray ------------------------------------------------------------------------------------
GRAY_HEAD = 1.22
GRAY_TORSO = [(10, -32.6), (0, -33.8), (-10, -33.6), (-18, -31.8), (-23.6, -27), (-25.4, -20), (-22.6, -13.6), (-14, -10.8),
              (-2, -9.6), (10, -10), (17, -12.4), (21, -17.4), (22.4, -24), (21, -30), (17, -33.6)]


def _gray_head(eyes):
    """The round, full-cheeked gray head in side view, centred near (9, -4) of its own space."""
    sil = _path([(-4.6, -7), (-.6, -14.4), (8, -17), (15.6, -14.4), (20.4, -8.6), (22.8, -3.2, .7), (22.4, 1.2), (19, 4.6),
                 (12, 7.2), (3.6, 7.4), (-2.6, 4.6), (-5.4, -1)])
    return (_ear((9.6, -15.2), (14.6, -24.4), (18, -11.6), GRAY_DK)
            + f'<path d="{sil}" fill="{GRAY}"/>'
            + _ear((-1, -12.4), (4, -25.4), (11.4, -16.4), GRAY, ((2.4, -15.2), (4.6, -22.6), (9, -16.2)), GRAY_EAR)
            + f'<path d="{_path([(-2.6, 4.6), (-5.6, 1), (-5.6, 6, 0), (-1, 7.6)])}" fill="{GRAY}"/>'
            + f'<path d="{_path([(14.4, -1.4), (19, -3.4), (22.6, -1.6), (21.6, 2.6), (17.6, 4.8), (13.2, 3.6)])}" fill="{GRAY_MZ}"/>'
            + eyes
            + f'<path d="M20.8,-3.8 L23.2,-3.2 L22,-1.6 Z" fill="{GRAY_NOSE}" stroke="{GRAY_NOSE}" stroke-width=".9" stroke-linejoin="round"/>'
            + f'<g stroke="{WHISK}" stroke-width=".5" stroke-linecap="round" opacity=".8">'
              '<path d="M19.4,0 L30,-2.6"/><path d="M19.6,1.4 L29.6,3"/></g>')


def _gray_front_leg(fill, cls=("", "")):
    paw = f'<ellipse cx="1.4" cy="3.4" rx="4.9" ry="2.8" fill="{fill}"/>'
    upper = f'<path d="{_tube([(0, -5), (.3, 5), (.3, 11.4)], 9.6, 7)}" fill="{fill}"/>'
    return _pivot(0, 0, upper + _pivot(.3, 11.4, paw, cls[1]), cls[0])


def _gray_hind_leg(fill, cls=("", "", "")):
    thigh = f'<path d="{_path([(-9, -5), (-1, -9.6), (7, -6), (8.6, 1.6), (5.6, 8), (1, 10.6), (-5, 8.6), (-9.4, 2.6)])}" fill="{fill}"/>'
    shin = f'<path d="{_tube([(0, -1), (-2.8, 2), (-5.6, 4.2)], 8, 6.4)}" fill="{fill}"/>'
    foot = (f'<path d="{_tube([(0, -1), (1.4, 3.4)], 6.4, 5.4)}" fill="{fill}"/>'
            f'<ellipse cx="2.4" cy="3.6" rx="4.9" ry="2.7" fill="{fill}"/>')
    return _pivot(0, 0, thigh + _pivot(2, 8.4, shin + _pivot(-5.6, 4.2, foot, cls[2]), cls[1]), cls[0])


def gray_run(k="gr", period=.36):
    """The chubby gray cat at a determined waddle-gallop, facing right, gold eyes wide open."""
    def legs(side, fill):
        hip, shoulder = (-11.6, -19) if side == "f" else (-15, -19), (10, -17.8) if side == "f" else (14, -17.8)
        return (_pivot(*hip, _gray_hind_leg(fill, (f"{k}h{side}1", f"{k}h{side}2", f"{k}h{side}3")))
                + _pivot(*shoulder, _gray_front_leg(fill, (f"{k}f{side}1", f"{k}f{side}2"))))

    tail = _pivot(-23, -25, f'<path d="{_tube([(0, 0), (-7, -1.4), (-12.6, -5.6), (-15.6, -12)], 7.6, 5.8)}" fill="{GRAY}"/>', f"{k}tl")
    body_d = _path(GRAY_TORSO)
    body = (f'<defs>{_clip(k + "b", body_d)}</defs><path d="{body_d}" fill="{GRAY}"/><g clip-path="url(#{k}b)">'
            f'<ellipse cx="-2" cy="-32" rx="20" ry="5" fill="{GRAY_LT}" opacity=".3"/>'
            f'<ellipse cx="0" cy="-7.6" rx="26" ry="5.4" fill="{GRAY_DK}" opacity=".7"/></g>')
    eye = (f'<circle cx="13.8" cy="-4.8" r="3.8" fill="{GOLD}" stroke="{GOLD_RIM}" stroke-width=".6"/>'
           f'<ellipse cx="14.5" cy="-4.8" rx="1.9" ry="3.1" fill="{PUPIL}"/><circle cx="13" cy="-6.3" r=".95" fill="#fff"/>')
    head = _pivot(15.4, -26.4, f'<g transform="scale({GRAY_HEAD})">{_gray_head(eye)}</g>', f"{k}hm")
    svg = (f'<g class="{k}bb"><g transform="translate(0,{FAR_UP})">{legs("f", GRAY_DK)}</g>{tail}{body}{legs("n", GRAY)}{head}</g>')
    gait = {name: [(f, a * .8) for f, a in GALLOP[name]] for name in ("f1", "f2", "h1", "h2", "h3")}
    gait |= {"tl": [(0, 6), (.4, -4), (.7, -8)], "hm": [(0, 3), (.4, 4), (.6, 0), (.85, -1)],
             "bb": [(0, (-.6, -2.4)), (.2, (-1, -1)), (.38, (-3, 0)), (.55, (-.4, 2.4)), (.7, (-.4, 1)), (.86, (-2.4, 0))]}
    return svg, _gait_css(k, period, gait, .12, ("tl", "hm", "bb"))


LEAF = ("M0,-6.5 C3.8,-4.2 4.2,1.2 0,6.5 C-4.2,1.2 -3.8,-4.2 0,-6.5 Z",
        "M0,-7 L1.6,-3 L5,-4 L3.4,-.6 L6,1 L2,2 L1.2,5.5 L0,4 L-1.2,5.5 L-2,2 L-6,1 L-3.4,-.6 L-5,-4 L-1.6,-3 Z")


def leaf(shape, fill, scale=1):
    """A fallen leaf centred on the origin, stem down."""
    return (f'<g transform="scale({scale:g})"><path d="{LEAF[shape]}" fill="{fill}"/>'
            f'<path d="M0,-5 L0,7.5" stroke="#000" stroke-opacity=".28" stroke-width=".7" stroke-linecap="round"/></g>')


def gray_sleep(k="gs", settle=None):
    """The chubby gray cat curled up asleep, head on the left resting on its paws, tail wrapped round, breathing.

    `settle` is (kind, seconds): "snow" piles up on its back, "leaf" drifts down onto it.
    """
    body_d = _path([(-22, -20), (-12, -28.6), (2, -31.6), (16, -29.4), (26, -22.4), (31, -12.6), (30, -4.4), (23, -.4), (4, 0),
                    (-14, 0), (-22, -6)])
    body = (f'<defs>{_clip(k + "c", body_d)}</defs><path d="{body_d}" fill="{GRAY}"/><g clip-path="url(#{k}c)">'
            f'<ellipse cx="4" cy="-29.6" rx="24" ry="6.6" fill="{GRAY_LT}" opacity=".5"/>'
            f'<ellipse cx="4" cy="1" rx="30" ry="6" fill="{GRAY_DK}" opacity=".6"/>'
            f'<path d="M26,-5 C30,-14 25,-24 13,-26.6" stroke="{GRAY_DK}" stroke-width="1.5" fill="none" stroke-linecap="round" opacity=".7"/></g>')
    kind, at = settle or (None, 0)
    if kind == "snow":
        body += _pivot(4, -31, '<path d="M-11,0 C-7,-4.6 6,-5.4 12,0 C6,1.2 -4,1.2 -11,0 Z" fill="#eef6ff"/>', f"{k}settle")
    elif kind == "leaf":
        body += _pivot(8, -31.2, f'<g transform="rotate(68)">{leaf(1, "#a65a30", 1.1)}</g>', f"{k}settle")
    breathing = _pivot(6, 0, f'<g transform="translate(-6,0)">{body}</g>', f"{k}br")
    tail_d = _tube([(30.4, -10), (29, -2.6), (18, 1.4), (4, 1.6), (-6, .4)], 7.8, 5.6)
    tail = (f'<path d="{tail_d}" fill="{GRAY}"/>'
            f'<path d="M30.6,-6.4 C28,-1.6 20,-1.4 6,-2" stroke="{GRAY_DK}" stroke-width="1.1" fill="none" stroke-linecap="round" opacity=".7"/>')
    paws = "".join(f'<ellipse cx="{x}" cy="-2.6" rx="5.4" ry="3.1" fill="{GRAY_LT}"/>'
                   f'<path d="M{x - 1.6},-.9 v-1.5 M{x + 1.4},-.9 v-1.5" stroke="{GRAY_DK}" stroke-width=".8" stroke-linecap="round"/>'
                   for x in (-26.4, -12))
    face = _path([(-19, -27), (-10, -24.6), (-4.4, -17), (-3.6, -9.4), (-7.6, -3.6), (-19, -1.6), (-30.4, -3.6), (-34.4, -9.4),
                  (-33.6, -17), (-28, -24.6)])
    head = (_ear((-33.4, -17.6), (-36.6, -31.4), (-25, -25.4), GRAY, ((-31.6, -19.6), (-34.4, -28.4), (-27, -24.6)), GRAY_EAR)
            + _ear((-13, -25.4), (-1.4, -31.4), (-4.6, -17.6), GRAY, ((-11, -24.6), (-3.6, -28.4), (-6.4, -19.6)), GRAY_EAR)
            + f'<path d="{face}" fill="{GRAY}"/>'
            + f'<ellipse cx="-19" cy="-22.4" rx="7.4" ry="2.6" fill="{GRAY_LT}" opacity=".55"/>'
            + f'<path d="{_path([(-19, -11), (-13.6, -10.6), (-10.8, -7), (-13.6, -3.8), (-19, -4.6), (-24.4, -3.8), (-27.2, -7), (-24.4, -10.6)])}" '
              f'fill="{GRAY_MZ}"/>'
            + f'<g stroke="{LID}" stroke-width="1.5" stroke-linecap="round" fill="none">'
              '<path d="M-29.4,-15 q3.2,2.8 6.4,0"/><path d="M-15,-15 q3.2,2.8 6.4,0"/></g>'
            + f'<path d="M-20.4,-11.2 L-17.6,-11.2 L-19,-9.6 Z" fill="{GRAY_NOSE}" stroke="{GRAY_NOSE}" stroke-width=".8" stroke-linejoin="round"/>'
            + f'<path d="M-19,-9.6 v.9 M-19,-8.7 q-1.2,1.1 -2.2,.3 M-19,-8.7 q1.2,1.1 2.2,.3" stroke="{LID}" stroke-width=".6" fill="none" stroke-linecap="round"/>'
            + f'<g stroke="{WHISK}" stroke-width=".5" stroke-linecap="round" opacity=".75">'
              '<path d="M-25,-8 L-37,-10"/><path d="M-25,-6.8 L-36.6,-5.4"/><path d="M-13,-8 L-1,-10"/><path d="M-13,-6.8 L-1.4,-5.4"/></g>')
    svg = f"{breathing}{tail}{paws}{head}"
    css = [f".{k}br{{animation:{k}breathe 3.6s ease-in-out infinite}}"
           f"@keyframes {k}breathe{{0%,100%{{transform:none}}50%{{transform:scale(1.015,1.06)}}}}"]
    if kind == "snow":
        css.append(f".{k}settle{{animation:{k}settle 2.4s ease-out {at:.2f}s both}}"
                   f"@keyframes {k}settle{{from{{transform:scale(.3,0);opacity:0}}}}")
    elif kind == "leaf":
        css.append(f".{k}settle{{animation:{k}settle 2.6s cubic-bezier(.3,.1,.3,1) {at:.2f}s both}}"
                   f"@keyframes {k}settle{{0%{{opacity:0;transform:translate(14px,-70px) rotate(-160deg)}}"
                   f"15%{{opacity:1}}45%{{transform:translate(-8px,-34px) rotate(40deg)}}"
                   f"75%{{transform:translate(5px,-10px) rotate(-25deg)}}100%{{transform:none}}}}")
    return svg, css
