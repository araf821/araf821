"""Vector cats for the contributions plate, drawn from Araf's two cats.

The ginger: soft ginger tabby, gentle darker stripes, cream muzzle and brows, a small white spot on the chest,
hazel-gold eyes, pink nose, tall ears. The gray: solid blue-gray, chubby cheeks, round gold eyes, dark nose.

Every pose is drawn in its own unit space with the ground at y=0. Side poses face right.
Each function returns (svg, css) with class names prefixed by `k` so poses can share a page.
"""

# ginger
FUR, FUR_LIT, STRIPE, FAR = "#dc8b4f", "#e9a56b", "#ac5f30", "#bb703f"
CREAM, WHITE, NOSE, EAR_IN = "#f2d8bb", "#f8efe4", "#e59d98", "#e8a9a3"
EYE, EYE_RIM, PUPIL = "#cdb556", "#6e4a1e", "#111111"
# gray
GRAY, GRAY_DK, GRAY_LT, GRAY_MZ = "#5c5f67", "#46484f", "#6e7179", "#73767e"
GRAY_EAR, GRAY_NOSE, GOLD, GOLD_RIM, LID, WHISK = "#6f6468", "#2c2e33", "#e8a72c", "#a86a14", "#25272c", "#a3a7ae"


def _pivot(x, y, inner, cls=""):
    """A group whose own origin sits at (x, y), so CSS rotations turn around that joint."""
    c = f' class="{cls}"' if cls else ""
    return f'<g transform="translate({x:g},{y:g})"><g{c}>{inner}</g></g>'


def _ear(pts, fill, inner=None, tuft=None):
    """A tall rounded ear; `inner` is the pink triangle, `tuft` adds two pale hairs."""
    a, b, c = pts
    out = (f'<path d="M{a[0]},{a[1]} L{b[0]},{b[1]} L{c[0]},{c[1]} Z" fill="{fill}" stroke="{fill}" '
           'stroke-width="3" stroke-linejoin="round"/>')
    if inner:
        ia, ib, ic = inner
        out += (f'<path d="M{ia[0]},{ia[1]} L{ib[0]},{ib[1]} L{ic[0]},{ic[1]} Z" fill="{EAR_IN}" stroke="{EAR_IN}" '
                'stroke-width="1.2" stroke-linejoin="round"/>')
    if tuft:
        out += f'<path d="{tuft}" stroke="{CREAM}" stroke-width=".6" stroke-linecap="round" fill="none" opacity=".8"/>'
    return out


def _leg(fill, paw_fill=None, rings=False):
    paw_fill = paw_fill or fill
    out = (f'<path d="M-6,-4 C-6,-8 6,-8 6,-4 L3.9,19 C3.6,21 -3.6,21 -3.9,19 Z" fill="{fill}"/>'
           f'<ellipse cx="1.4" cy="21.4" rx="5.4" ry="3.5" fill="{paw_fill}"/>')
    if rings:
        out += f'<path d="M-4.8,6 h4.4 M-4.4,12 h4" stroke="{STRIPE}" stroke-width="1.8" stroke-linecap="round"/>'
    return out


def _tail(d, w=7.5):
    return (f'<path d="{d}" fill="none" stroke="{FUR}" stroke-width="{w}" stroke-linecap="round"/>'
            f'<path d="{d}" fill="none" stroke="{STRIPE}" stroke-width="{w}" stroke-dasharray="2.6 5" '
            'stroke-dashoffset="-3" opacity=".85"/>')


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
    band = _knit(paint, "M16,-45 C20,-47.5 27.5,-44 31.5,-38 L28.6,-34.2 C25,-39.5 20,-41.8 14.6,-40.4 Z")
    if flowing:
        tail = _pivot(18, -42, _knit(paint, "M0,0 C-6,-2.4 -12,-1 -19,-4.6 L-17.6,1 C-11,3 -5,3.4 0,4.6 Z")
                      + _fringe(base, (-18.8, -3.8), (-17.8, .4), (-2.6, .4), 3), f"{k}scarf")
    else:
        tail = _pivot(20, -39.5, _knit(paint, "M0,0 L4.6,.4 L3.6,12.6 L-.8,12 Z") + _fringe(base, (-.4, 12.2), (3.4, 12.6), (0, 2.6)))
    return defs + tail + band


HAT_TRIM = "#f6f1ea"


def _side_hat(color):
    """A floppy knit hat on the side-view head, its tip trailing back to a pom-pom."""
    return (f'<path d="M.6,-16.6 L17.4,-19.8 C14,-27.4 4,-33.6 -10.6,-33.4 C-4.6,-29.6 -1.4,-23.6 .6,-16.6 Z" fill="{color}"/>'
            f'<path d="M-.4,-15 L18.4,-18.4 L17.4,-22.6 L-1.2,-19.4 Z" fill="{HAT_TRIM}" stroke="{HAT_TRIM}" stroke-width="2" stroke-linejoin="round"/>'
            f'<circle cx="-10.8" cy="-33.4" r="3.6" fill="{HAT_TRIM}"/>')


def _front_hat(color):
    """The same hat seen from the front, leaning off to one side."""
    return (f'<path d="M-11,-62 C-8.6,-74 2,-83 15.4,-81 C10.6,-77.6 8.6,-71 9.4,-62 Z" fill="{color}"/>'
            f'<path d="M-2,-63 C1,-71 6,-77 12,-79.6" stroke="#000" stroke-opacity=".14" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
            f'<rect x="-13" y="-65" width="24.4" height="6.6" rx="3.3" fill="{HAT_TRIM}"/>'
            f'<circle cx="15.8" cy="-81" r="4" fill="{HAT_TRIM}"/>')


# ---- the ginger, side view ---------------------------------------------------------------------
def _side_body(k):
    shapes = ('<ellipse cx="0" cy="-30" rx="27" ry="13.5"/><circle cx="-17" cy="-29" r="13"/>'
              '<circle cx="17" cy="-31" r="12.5"/><ellipse cx="24" cy="-40" rx="9" ry="11"/>')
    clip = f'<clipPath id="{k}b">{shapes}</clipPath>'
    marks = (f'<g clip-path="url(#{k}b)">'
             f'<ellipse cx="2" cy="-19.5" rx="26" ry="5.5" fill="{FUR_LIT}" opacity=".35"/>'
             f'<ellipse cx="22" cy="-27" rx="5" ry="6.5" fill="{FUR_LIT}"/>'
             f'<ellipse cx="23.5" cy="-27" rx="1.8" ry="2.8" fill="{WHITE}"/>'
             f'<g stroke="{STRIPE}" stroke-width="3" stroke-linecap="round" opacity=".9">'
             + "".join(f'<path d="M{x},-46 L{x - 3},{-35 + abs(x) * .04:.1f}"/>' for x in (-26, -19, -12, -5, 2, 9))
             + '<path d="M-31,-23 Q-21,-27 -12,-21" fill="none"/><path d="M-30,-17 Q-21,-21 -13,-16" fill="none"/></g></g>')
    return f'<defs>{clip}</defs><g fill="{FUR}">{shapes}</g>{marks}'


def _side_head(k, hat=None):
    clip = f'<clipPath id="{k}h"><ellipse cx="9" cy="-8" rx="13" ry="12.5"/></clipPath>'
    return (f"<defs>{clip}</defs>"
            + _ear(((10, -17), (15.5, -31.5), (19.5, -14)), FAR)
            + f'<ellipse cx="9" cy="-8" rx="13" ry="12.5" fill="{FUR}"/>'
            + f'<ellipse cx="14.5" cy="-3" rx="9" ry="7.2" fill="{FUR}"/>'
            + _ear(((1.5, -15), (4.5, -31.5), (13.5, -18.5)), FUR, ((4.4, -18), (5.9, -27.4), (10.4, -19)),
                   "M6,-19.5 l.6,-4 M8,-19.5 l.2,-3.4")
            + f'<g clip-path="url(#{k}h)">'
              f'<ellipse cx="13" cy="-13.5" rx="4.6" ry="2.4" fill="{FUR_LIT}"/>'
              f'<g stroke="{STRIPE}" stroke-width="1.7" stroke-linecap="round">'
              '<path d="M4.5,-20 L5.2,-15"/><path d="M8,-21 L8.3,-16"/><path d="M11.5,-20.5 L11,-16"/>'
              '<path d="M1,-8.5 L5.5,-7.8"/><path d="M1.2,-5 L5,-5"/></g></g>'
            + f'<ellipse cx="18.5" cy="-1.6" rx="6.4" ry="4.8" fill="{CREAM}"/>'
            + f'<path d="M22.6,-5.6 L25.4,-5.6 L24,-3.8 Z" fill="{NOSE}" stroke="{NOSE}" stroke-width="1" stroke-linejoin="round"/>'
            + f'<ellipse cx="14.6" cy="-9" rx="2.8" ry="3.3" fill="{EYE}" stroke="{EYE_RIM}" stroke-width=".5"/>'
            + f'<ellipse cx="15.1" cy="-9" rx="1.5" ry="2.8" fill="{PUPIL}"/>'
            + '<circle cx="14" cy="-10.4" r=".8" fill="#fff"/>'
            + f'<g stroke="{WHITE}" stroke-width=".6" stroke-linecap="round" opacity=".75">'
              '<path d="M21,-2.2 L32,-5"/><path d="M21,-.8 L32,.2"/><path d="M20.6,.4 L30,3"/></g>'
            + (_side_hat(hat) if hat else ""))


def tabby_run(k="tr", period=.3, scarf=None, hat=None):
    """Side view, mid-gallop: legs, body and tail on one stride loop."""
    far = _pivot(12, -24, _leg(FAR), f"{k}ff") + _pivot(-21, -23, _leg(FAR), f"{k}bf")
    near = _pivot(17, -24, _leg(FUR, rings=True), f"{k}fn") + _pivot(-15, -23, _leg(FUR, rings=True), f"{k}bn")
    tail = _pivot(-27, -35, _tail("M0,0 C-10,-2 -19,-8 -24,-18"), f"{k}t")
    head = _pivot(26, -42, _side_head(k, hat))
    wrap = _side_scarf(scarf, k, True) if scarf else ""
    svg = f'<g class="{k}bob">{far}{tail}{_side_body(k)}{near}{wrap}{head}</g>'
    p = period
    css = [
        f".{k}fn,.{k}ff,.{k}bn,.{k}bf,.{k}t,.{k}bob{{animation:{p}s linear infinite}}",
        f".{k}fn{{animation-name:{k}fr}}.{k}ff{{animation-name:{k}fr;animation-delay:-{p * .12:.3f}s}}",
        f".{k}bn{{animation-name:{k}br}}.{k}bf{{animation-name:{k}br;animation-delay:-{p * .12:.3f}s}}",
        f"@keyframes {k}fr{{0%{{transform:rotate(-52deg)}}45%{{transform:rotate(38deg)}}100%{{transform:rotate(-52deg)}}}}",
        f"@keyframes {k}br{{0%{{transform:rotate(44deg)}}50%{{transform:rotate(-42deg)}}100%{{transform:rotate(44deg)}}}}",
        f".{k}t{{animation-name:{k}tl}}@keyframes {k}tl{{0%,100%{{transform:rotate(-8deg)}}50%{{transform:rotate(10deg)}}}}",
        f".{k}bob{{animation-name:{k}bb}}@keyframes {k}bb{{0%,100%{{transform:translate(0,0) rotate(0)}}"
        f"25%{{transform:translate(0,-4px) rotate(-3deg)}}75%{{transform:translate(0,-2px) rotate(3deg)}}}}",
        f".{k}scarf{{animation:{k}flap {p * 1.5:.2f}s ease-in-out infinite}}"
        f"@keyframes {k}flap{{0%,100%{{transform:rotate(-6deg) scale(1,1)}}50%{{transform:rotate(7deg) scale(.94,1.12)}}}}",
    ]
    return svg, css


def tabby_stand(k="ts", look_at=None, look_back=.18, scarf=None, hat=None):
    """Side view standing; at `look_at` seconds the head turns back over the shoulder."""
    far = _pivot(12, -24, _leg(FAR)) + _pivot(-20, -23, _leg(FAR))
    near = _pivot(18, -24, _leg(FUR, rings=True)) + _pivot(-14, -23, _leg(FUR, rings=True))
    tail = _pivot(-27, -35, _tail("M0,0 C-8,-6 -10,-20 -4,-30 C-1,-34 3,-34 4,-31"))
    head = _pivot(26, -42, _side_head(k, hat), f"{k}head")
    wrap = _side_scarf(scarf, k, False) if scarf else ""
    svg = f"{far}{tail}{_side_body(k)}{near}{wrap}{head}"
    css = []
    if look_at is not None:
        css.append(f".{k}head{{animation:{k}look {look_back}s cubic-bezier(.3,0,.2,1) {look_at:.2f}s both}}"
                   f"@keyframes {k}look{{from{{transform:none}}to{{transform:translate(-3px,-2px) scale(-1,1)}}}}")
    return svg, css


# ---- the ginger, sitting and facing us -----------------------------------------------------------
def tabby_front(k="tf", blink_every=4.2, delay=0, scarf=None, hat=None):
    """Facing us, sitting, tail up its side; blinks now and then."""
    body_d = "M-14.5,-40 C-21.5,-28 -23.5,-8 -18,-2 Q0,3 18,-2 C23.5,-8 21.5,-28 14.5,-40 Z"
    clip = (f'<clipPath id="{k}b"><path d="{body_d}"/></clipPath>'
            f'<clipPath id="{k}h"><ellipse cx="0" cy="-50.5" rx="16" ry="14.5"/></clipPath>')
    body = (f'<path d="{body_d}" fill="{FUR}"/>'
            f'<g clip-path="url(#{k}b)">'
            f'<ellipse cx="0" cy="-34" rx="11" ry="10" fill="{FUR_LIT}"/>'
            f'<g stroke="{STRIPE}" stroke-width="2.6" stroke-linecap="round" fill="none" opacity=".9">'
            '<path d="M-23,-34 Q-17,-32 -14.5,-28"/><path d="M-24,-27 Q-18,-25.5 -15.5,-21"/>'
            '<path d="M23,-34 Q17,-32 14.5,-28"/><path d="M24,-27 Q18,-25.5 15.5,-21"/>'
            '<path d="M-6,-38 Q0,-35.6 6,-38"/></g>'
            f'<path d="M0,-33 C-2.4,-30 -2,-25.5 0,-23.5 C2,-25.5 2.4,-30 0,-33 Z" fill="{WHITE}"/></g>')
    base = "".join(
        f'<ellipse cx="{sx * 14}" cy="-9.5" rx="9.5" ry="10" fill="{FUR}"/>'
        f'<path d="M{sx * 21},-15.5 Q{sx * 15.5},-14 {sx * 13.5},-8.5" stroke="{STRIPE}" stroke-width="2.4" fill="none" stroke-linecap="round"/>'
        f'<path d="M{sx * 22},-10 Q{sx * 18},-9 {sx * 16.5},-5" stroke="{STRIPE}" stroke-width="2.2" fill="none" stroke-linecap="round"/>'
        f'<ellipse cx="{sx * 18.6}" cy="-2.8" rx="5.2" ry="3.1" fill="{FUR}"/>'
        f'<path d="M{sx * 14.6},-1.4 Q{sx * 18.6},.5 {sx * 22.6},-1.4" stroke="{FAR}" stroke-width="1" fill="none" stroke-linecap="round"/>'
        for sx in (-1, 1))
    gap = f'<path d="M-1.8,-21 L1.8,-21 L2.2,-3 L-2.2,-3 Z" fill="{FAR}"/>'
    legs = "".join(
        f'<path d="M{x - 4.2},-20 C{x - 4.2},-25.5 {x + 4.2},-25.5 {x + 4.2},-20 L{x + 4},-5 L{x - 4},-5 Z" fill="{FUR_LIT}"/>'
        f'<path d="M{x + sx * 4.1},-15 h{-sx * 3.2} M{x + sx * 4},-10 h{-sx * 2.8}" stroke="{STRIPE}" stroke-width="1.6" stroke-linecap="round"/>'
        f'<ellipse cx="{x}" cy="-3.5" rx="5.3" ry="3.5" fill="{FUR_LIT}"/>'
        f'<path d="M{x - 1.5},-1.2 v-1.7 M{x + 1.5},-1.2 v-1.7" stroke="{FAR}" stroke-width=".9" stroke-linecap="round"/>'
        for x, sx in ((-6.2, -1), (6.2, 1)))
    tail = _pivot(14, -6, _tail("M0,0 C9,1 15,-6 15,-17 C15,-24 19,-28 23,-27", 5.8), f"{k}tail")
    ears = "".join(_ear(((s * 15.5, -56), (s * 15.5, -75), (s * 4, -63)), FUR,
                        ((s * 13.4, -59.6), (s * 13.6, -70.5), (s * 7.4, -62.8)),
                        f"M{s * 11.5},-61.5 l{s * 1.4},-4.4 M{s * 9.5},-62 l{s * 1.8},-3.2")
                   for s in (-1, 1))
    eyes = "".join(
        _pivot(s * 6.8, -52.5,
               f'<ellipse rx="3.6" ry="3.6" fill="{EYE}" stroke="{EYE_RIM}" stroke-width=".55"/>'
               f'<ellipse rx="2" ry="3" fill="{PUPIL}"/><circle cx="-1" cy="-1.4" r=".95" fill="#fff"/>', f"{k}eye")
        for s in (-1, 1))
    head = (ears
            + f'<ellipse cx="0" cy="-46.5" rx="18.2" ry="10.5" fill="{FUR}"/>'
            + f'<ellipse cx="0" cy="-50.5" rx="16" ry="14.5" fill="{FUR}"/>'
            + f'<g clip-path="url(#{k}h)">'
              f'<ellipse cx="-6.8" cy="-57.2" rx="4.2" ry="2.2" fill="{FUR_LIT}"/><ellipse cx="6.8" cy="-57.2" rx="4.2" ry="2.2" fill="{FUR_LIT}"/>'
              f'<path d="M0,-63 L0,-48" stroke="{FUR_LIT}" stroke-width="3.2" stroke-linecap="round"/>'
              f'<g stroke="{STRIPE}" stroke-width="1.7" stroke-linecap="round">'
              '<path d="M-2.4,-65 L-2,-58.5"/><path d="M2.4,-65 L2,-58.5"/><path d="M-6.2,-63.6 L-5,-59.6"/><path d="M6.2,-63.6 L5,-59.6"/>'
              '<path d="M-10.4,-50.6 L-15.4,-51.4"/><path d="M10.4,-50.6 L15.4,-51.4"/></g></g>'
            + f'<g stroke="{STRIPE}" stroke-width="1.6" stroke-linecap="round">'
              '<path d="M-18,-47.6 L-12.6,-46.8"/><path d="M-17.6,-44.2 L-12.6,-44.4"/>'
              '<path d="M18,-47.6 L12.6,-46.8"/><path d="M17.6,-44.2 L12.6,-44.4"/></g>'
            + f'<ellipse cx="-3.4" cy="-44.2" rx="4.4" ry="3.6" fill="{CREAM}"/><ellipse cx="3.4" cy="-44.2" rx="4.4" ry="3.6" fill="{CREAM}"/>'
            + f'<ellipse cx="0" cy="-40.8" rx="3.4" ry="2.5" fill="{CREAM}"/>'
            + eyes
            + f'<path d="M-2.2,-47.4 L2.2,-47.4 L0,-45 Z" fill="{NOSE}" stroke="{NOSE}" stroke-width="1.2" stroke-linejoin="round"/>'
            + f'<path d="M0,-45 v1.2 M0,-43.8 q-1.5,1.5 -2.8,.4 M0,-43.8 q1.5,1.5 2.8,.4" stroke="{FAR}" stroke-width=".75" '
              'fill="none" stroke-linecap="round"/>'
            + f'<g stroke="{WHITE}" stroke-width=".6" stroke-linecap="round" opacity=".75">'
              '<path d="M-7,-44.4 L-21,-47"/><path d="M-7,-43 L-21,-42.6"/><path d="M-7,-41.8 L-19.5,-38.6"/>'
              '<path d="M7,-44.4 L21,-47"/><path d="M7,-43 L21,-42.6"/><path d="M7,-41.8 L19.5,-38.6"/></g>')
    wrap = ""
    if scarf:
        defs, paint, colour = _paint(scarf, k)
        wrap = (defs + _knit(paint, "M6,-33 L11.6,-34 L12.8,-19.4 L7,-18.6 Z") + _fringe(colour, (7.4, -19), (12.4, -19.4), (0, 2.6))
                + _knit(paint, "M-15,-39.6 Q0,-32.6 15,-39.6 L15.4,-33.8 Q0,-26.6 -15.4,-33.8 Z"))
    topper = _front_hat(hat) if hat else ""
    svg = f"<defs>{clip}</defs>{tail}{body}{base}{gap}{legs}{wrap}{head}{topper}"
    T = blink_every
    css = [f".{k}eye{{animation:{k}blink {T}s {delay + 1.2:.2f}s infinite}}"
           f"@keyframes {k}blink{{0%,92%,100%{{transform:none}}95%{{transform:scale(1,.12)}}}}",
           f".{k}tail{{animation:{k}flick 3.4s ease-in-out {delay + .6:.2f}s infinite}}"
           f"@keyframes {k}flick{{0%,70%,100%{{transform:none}}80%{{transform:rotate(-7deg)}}90%{{transform:rotate(3deg)}}}}"]
    return svg, css


# ---- the gray ------------------------------------------------------------------------------------
def _stub(fill, h=12):
    return (f'<path d="M-5,-3 C-5,-6.5 5,-6.5 5,-3 L4,{h - 2} C3.7,{h} -3.7,{h} -4,{h - 2} Z" fill="{fill}"/>'
            f'<ellipse cx="1.2" cy="{h - .6}" rx="5" ry="3.2" fill="{fill}"/>')


def _gray_ear(a, b, c, fill, inner):
    ia, ib, ic = inner
    return (f'<path d="M{a[0]},{a[1]} L{b[0]},{b[1]} L{c[0]},{c[1]} Z" fill="{fill}" stroke="{fill}" stroke-width="3" stroke-linejoin="round"/>'
            f'<path d="M{ia[0]},{ia[1]} L{ib[0]},{ib[1]} L{ic[0]},{ic[1]} Z" fill="{GRAY_EAR}" stroke="{GRAY_EAR}" '
            'stroke-width="1" stroke-linejoin="round"/>')


def gray_run(k="gr", period=.36):
    """The chubby gray cat at a determined waddle-run, facing right, gold eyes wide open."""
    far = _pivot(11, -11, _stub(GRAY_DK), f"{k}ff") + _pivot(-17, -11, _stub(GRAY_DK), f"{k}bf")
    near = _pivot(15, -11, _stub(GRAY), f"{k}fn") + _pivot(-12, -11, _stub(GRAY), f"{k}bn")
    tail = _pivot(-26, -20, f'<path d="M0,0 C-8,-2 -14,-8 -16,-16" fill="none" stroke="{GRAY}" stroke-width="7" stroke-linecap="round"/>', f"{k}t")
    body = (f'<ellipse cx="0" cy="-18" rx="27" ry="15.5" fill="{GRAY}"/>'
            f'<ellipse cx="-2" cy="-25" rx="21" ry="6" fill="{GRAY_LT}" opacity=".45"/>'
            f'<path d="M-22,-10 Q0,0 24,-10 Q20,-3 0,-2.6 Q-16,-3 -22,-10 Z" fill="{GRAY_DK}"/>'
            f'<g stroke="{GRAY_DK}" stroke-width="1" stroke-linecap="round" fill="none" opacity=".3">'
            '<path d="M-10,-31.5 q1.4,3 .8,6"/><path d="M-2,-32.6 q1.4,3 .8,6"/></g>')
    head = _pivot(22, -25, (
        _gray_ear((6, -9), (11.5, -22), (16, -7), GRAY_DK, ((8.4, -9.4), (11.4, -18), (13.6, -8.6)))
        + f'<ellipse cx="8" cy="-3" rx="13" ry="11.5" fill="{GRAY}"/>'
        + f'<ellipse cx="11" cy="3.2" rx="10" ry="6" fill="{GRAY}"/>'
        + _gray_ear((-.5, -8), (1.5, -21.5), (9.5, -11), GRAY, ((1.6, -10.4), (2.8, -18), (6.8, -11.6)))
        + f'<ellipse cx="4.5" cy="-11" rx="5" ry="2.6" fill="{GRAY_LT}" opacity=".6"/>'
        + f'<ellipse cx="15.5" cy="1.6" rx="6" ry="4.4" fill="{GRAY_MZ}"/>'
        + f'<circle cx="12.6" cy="-4.6" r="3.2" fill="{GOLD}" stroke="{GOLD_RIM}" stroke-width=".6"/>'
        + f'<ellipse cx="13.3" cy="-4.6" rx="1.7" ry="2.6" fill="{PUPIL}"/>'
        + '<circle cx="12" cy="-5.9" r=".8" fill="#fff"/>'
        + f'<path d="M19.6,-1.4 L21.8,-1.4 L20.7,0 Z" fill="{GRAY_NOSE}" stroke="{GRAY_NOSE}" stroke-width=".8" stroke-linejoin="round"/>'
        + f'<g stroke="{WHISK}" stroke-width=".55" stroke-linecap="round" opacity=".8">'
          '<path d="M18,2 L29,0"/><path d="M18,3.4 L28.5,4.6"/></g>'))
    svg = f'<g class="{k}bob">{far}{tail}{body}{near}{head}</g>'
    q = period
    css = [
        f".{k}fn,.{k}ff,.{k}bn,.{k}bf,.{k}t,.{k}bob{{animation:{q}s linear infinite}}",
        f".{k}fn{{animation-name:{k}fr}}.{k}ff{{animation-name:{k}fr;animation-delay:-{q / 2:.3f}s}}",
        f".{k}bn{{animation-name:{k}br}}.{k}bf{{animation-name:{k}br;animation-delay:-{q / 2:.3f}s}}",
        f"@keyframes {k}fr{{0%,100%{{transform:rotate(-38deg)}}50%{{transform:rotate(32deg)}}}}",
        f"@keyframes {k}br{{0%,100%{{transform:rotate(34deg)}}50%{{transform:rotate(-34deg)}}}}",
        f".{k}t{{animation-name:{k}tl}}@keyframes {k}tl{{0%,100%{{transform:rotate(-6deg)}}50%{{transform:rotate(8deg)}}}}",
        f".{k}bob{{animation-name:{k}bb}}@keyframes {k}bb{{0%,100%{{transform:translate(0,0) rotate(1.5deg)}}"
        f"50%{{transform:translate(0,-3px) rotate(-1.5deg)}}}}",
    ]
    return svg, css


LEAF = ("M0,-6.5 C3.8,-4.2 4.2,1.2 0,6.5 C-4.2,1.2 -3.8,-4.2 0,-6.5 Z",
        "M0,-7 L1.6,-3 L5,-4 L3.4,-.6 L6,1 L2,2 L1.2,5.5 L0,4 L-1.2,5.5 L-2,2 L-6,1 L-3.4,-.6 L-5,-4 L-1.6,-3 Z")


def leaf(shape, fill, scale=1):
    """A fallen leaf centred on the origin, stem down."""
    return (f'<g transform="scale({scale:g})"><path d="{LEAF[shape]}" fill="{fill}"/>'
            f'<path d="M0,-5 L0,7.5" stroke="#000" stroke-opacity=".28" stroke-width=".7" stroke-linecap="round"/></g>')


def gray_sleep(k="gs", settle=None):
    """`settle` is (kind, seconds): "snow" piles up on its back, "leaf" drifts down onto it."""
    """The chubby gray cat curled up asleep, head on the left, paws tucked, breathing."""
    clip = f'<clipPath id="{k}c"><ellipse cx="0" cy="-15.5" rx="30" ry="15.5"/></clipPath>'
    body = (f'<ellipse cx="0" cy="-15.5" rx="30" ry="15.5" fill="{GRAY}"/>'
            f'<g clip-path="url(#{k}c)">'
            f'<ellipse cx="2" cy="-25" rx="25" ry="7.5" fill="{GRAY_LT}" opacity=".5"/>'
            f'<path d="M-30,-8 Q0,3 30,-9 L30,2 L-30,2 Z" fill="{GRAY_DK}"/>'
            f'<path d="M24,-5 C28,-14 22,-24 12,-26" stroke="{GRAY_DK}" stroke-width="1.5" fill="none" stroke-linecap="round" opacity=".8"/>'
            f'<g stroke="{GRAY_DK}" stroke-width="1" stroke-linecap="round" fill="none" opacity=".3">'
            '<path d="M0,-30.5 q1.4,3 .6,6"/><path d="M7,-30 q1.4,3 .6,5.6"/></g></g>')
    kind, at = settle or (None, 0)
    if kind == "snow":
        body += _pivot(4, -29.6, '<path d="M-11,0 C-7,-4.6 6,-5.4 12,0 C6,1.2 -4,1.2 -11,0 Z" fill="#eef6ff"/>', f"{k}settle")
    elif kind == "leaf":
        body += _pivot(8, -30.5, f'<g transform="rotate(68)">{leaf(1, "#a65a30", 1.1)}</g>', f"{k}settle")
    breathing = _pivot(6, 0, f'<g transform="translate(-6,0)">{body}</g>', f"{k}br")
    tail = (f'<path d="M33,-7 C36,0 22,3 6,2.4 C-2,2 -8,1 -12,-.6" fill="none" stroke="{GRAY_DK}" stroke-width="7.4" stroke-linecap="round"/>'
            f'<path d="M30,-1.6 C24,1.4 14,2.4 6,2.2" fill="none" stroke="{GRAY}" stroke-width="2" stroke-linecap="round" opacity=".55"/>')
    paws = "".join(f'<ellipse cx="{x}" cy="-3" rx="5.4" ry="3.2" fill="{GRAY_LT}"/>'
                   f'<path d="M{x - 1.6},-1.2 v-1.6 M{x + 1.4},-1.2 v-1.6" stroke="{GRAY_DK}" stroke-width=".8" stroke-linecap="round"/>'
                   for x in (-14, -6.5))
    head = (_gray_ear((-31.5, -19), (-33.5, -32), (-23, -24.5), GRAY, ((-30, -21.6), (-31.5, -29), (-25.4, -24.2)))
            + _gray_ear((-19, -24.5), (-12, -33), (-9.5, -20), GRAY, ((-17.2, -23.8), (-12.8, -29.6), (-11.8, -21.8)))
            + f'<ellipse cx="-21" cy="-13" rx="14.5" ry="12" fill="{GRAY}"/>'
            + f'<ellipse cx="-21" cy="-8" rx="15.5" ry="7" fill="{GRAY}"/>'
            + f'<ellipse cx="-21" cy="-21" rx="7" ry="2.8" fill="{GRAY_LT}" opacity=".55"/>'
            + f'<g stroke="{GRAY_DK}" stroke-width="1" stroke-linecap="round" opacity=".4">'
              '<path d="M-23.6,-24 l.3,3.4"/><path d="M-21,-24.6 v3.6"/><path d="M-18.4,-24 l-.3,3.4"/></g>'
            + f'<ellipse cx="-21" cy="-7.4" rx="6.4" ry="4" fill="{GRAY_MZ}"/>'
            + f'<g stroke="{LID}" stroke-width="1.6" stroke-linecap="round" fill="none">'
              '<path d="M-30.4,-14.2 q3.2,2.6 6.4,0"/><path d="M-18,-14.2 q3.2,2.6 6.4,0"/></g>'
            + f'<g stroke="{LID}" stroke-width=".7" stroke-linecap="round" opacity=".8">'
              '<path d="M-30,-13 l-1.4,1"/><path d="M-11.9,-13 l1.4,1"/></g>'
            + f'<path d="M-22.4,-9.8 L-19.6,-9.8 L-21,-8.2 Z" fill="{GRAY_NOSE}" stroke="{GRAY_NOSE}" stroke-width=".8" stroke-linejoin="round"/>'
            + f'<path d="M-21,-8.2 v.9 M-21,-7.3 q-1.2,1.1 -2.2,.3 M-21,-7.3 q1.2,1.1 2.2,.3" stroke="{LID}" stroke-width=".6" fill="none" stroke-linecap="round"/>'
            + f'<g stroke="{WHISK}" stroke-width=".55" stroke-linecap="round" opacity=".75">'
              '<path d="M-27,-7.6 L-38,-9.4"/><path d="M-27,-6.4 L-37.5,-5"/><path d="M-15,-7.6 L-4,-9.4"/><path d="M-15,-6.4 L-4.5,-5"/></g>')
    svg = f"<defs>{clip}</defs>{breathing}{tail}{paws}{head}"
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
