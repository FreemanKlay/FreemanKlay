"""Drawing kit for the wire scenes: poles (with crossarms, insulators, transformer, lamp, lattice tower),
wire chains with sag, and light streaks that travel along a wire.

A streak is a stack of dashes on the same wire, all sharing one head: a short bright core followed by
longer, fainter tails, plus a wide faint layer for the glow. No filters, so it draws the same everywhere.
"""
import math

from common import for_light, mix, theme

TAIL_MAX = 170


# ---------------------------------------------------------------- geometry
def _seg_len(p, c, q, n=24):
    pts = []
    for i in range(n + 1):
        t = i / n
        u = 1 - t
        pts.append((u * u * p[0] + 2 * u * t * c[0] + t * t * q[0], u * u * p[1] + 2 * u * t * c[1] + t * t * q[1]))
    return sum(math.dist(pts[i], pts[i + 1]) for i in range(n))


class Chain:
    """A wire made of quadratic segments through given points; each span gets its own sag."""

    def __init__(self, points, sags):
        self.segs = []
        for (p, q), sag in zip(zip(points, points[1:]), sags):
            self.segs.append((p, ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + sag), q))
        self.length = sum(_seg_len(*s) for s in self.segs)

    def d(self):
        out = "M%.1f %.1f" % self.segs[0][0]
        for _, c, q in self.segs:
            out += "Q%.1f %.1f %.1f %.1f" % (c + q)
        return out


def wire_chain(attach_rows, lead_in=None, tail=None, sag_k=0.10, lane=0):
    """attach_rows: list of (x, y) in order. lead_in / tail: extra points before / after."""
    pts = list(attach_rows)
    sags = []
    if lead_in:
        pts = [lead_in] + pts
        sags.append(max(10, abs(pts[1][0] - pts[0][0]) * (0.07 + 0.006 * lane)))
    for a, b in zip(attach_rows, attach_rows[1:]):
        dx = math.dist(a, b)
        sags.append(dx * (sag_k + 0.012 * lane))
    if tail:
        pts = pts + [tail]
        sags.append(4)
    return Chain(pts, sags)


# ---------------------------------------------------------------- poles
def pole(x, base, h, mode, kind="plain", fade=1.0):
    """Returns (svg, attach points). kind: plain | transformer | lamp | tower. Silhouette in the pole colour."""
    T = theme(mode)
    col = T["pole"]
    s = h / 206
    top = base - h
    sw = max(0.7, 1.4 * s)
    parts = []
    if kind == "tower":
        w0, w1 = 22 * s, 9 * s
        parts.append(f'<path d="M{x - w0:.1f} {base:.1f}L{x - w1:.1f} {top:.1f}M{x + w0:.1f} {base:.1f}L{x + w1:.1f} {top:.1f}" fill="none" stroke="{col}" stroke-width="{max(.9, 2 * s):.1f}"/>')
        n = 7
        lat = ""
        for i in range(n):
            y0 = base - h * i / n
            y1 = base - h * (i + 1) / n
            xa0, xa1 = w0 + (w1 - w0) * i / n, w0 + (w1 - w0) * (i + 1) / n
            lat += f"M{x - xa0:.1f} {y0:.1f}L{x + xa1:.1f} {y1:.1f}M{x + xa0:.1f} {y0:.1f}L{x - xa1:.1f} {y1:.1f}M{x - xa1:.1f} {y1:.1f}H{x + xa1:.1f}"
        parts.append(f'<path d="{lat}" fill="none" stroke="{col}" stroke-width="{max(.6, 1 * s):.1f}"/>')
        parts.append(f'<path d="M{x:.1f} {top:.1f}V{top - 14 * s:.1f}" stroke="{col}" stroke-width="{max(.8, 1.4 * s):.1f}"/>')
    else:
        wt, wb = max(1.6, 4.4 * s), max(2.4, 7.2 * s)
        parts.append(f'<path d="M{x - wt / 2:.1f} {top:.1f}L{x + wt / 2:.1f} {top:.1f}L{x + wb / 2:.1f} {base:.1f}L{x - wb / 2:.1f} {base:.1f}Z" fill="{col}"/>')
    attach = []

    def arm(y, half):
        th = max(1.3, 3.6 * s)
        parts.append(f'<rect x="{x - half:.1f}" y="{y:.1f}" width="{2 * half:.1f}" height="{th:.1f}" rx="{th / 2:.1f}" fill="{col}"/>')
        parts.append(f'<path d="M{x:.1f} {y + 20 * s:.1f}L{x - half * .62:.1f} {y + th:.1f}M{x:.1f} {y + 20 * s:.1f}L{x + half * .62:.1f} {y + th:.1f}" fill="none" stroke="{col}" stroke-width="{sw:.1f}"/>')
        for dx in (-0.86, 0, 0.86):
            ix = x + half * dx
            parts.append(f'<rect x="{ix - 1.3 * s:.1f}" y="{y - 6 * s:.1f}" width="{2.6 * s:.1f}" height="{6.4 * s:.1f}" fill="{col}"/>'
                         f'<circle cx="{ix:.1f}" cy="{y - 6.4 * s:.1f}" r="{max(.9, 2 * s):.1f}" fill="{col}"/>')
            attach.append((ix, y - 7 * s))

    arm(top + 0.07 * h, 46 * s)
    arm(top + 0.30 * h, 34 * s)
    if kind == "transformer":
        ty = top + 0.46 * h
        parts.append(f'<rect x="{x + 6 * s:.1f}" y="{ty:.1f}" width="{19 * s:.1f}" height="{32 * s:.1f}" rx="{4 * s:.1f}" fill="{col}"/>'
                     f'<rect x="{x + 11 * s:.1f}" y="{ty - 4 * s:.1f}" width="{3 * s:.1f}" height="{5 * s:.1f}" fill="{col}"/>'
                     f'<rect x="{x + 18 * s:.1f}" y="{ty - 4 * s:.1f}" width="{3 * s:.1f}" height="{5 * s:.1f}" fill="{col}"/>'
                     f'<path d="M{x:.1f} {ty + 6 * s:.1f}H{x + 6 * s:.1f}M{x:.1f} {ty + 26 * s:.1f}H{x + 6 * s:.1f}" stroke="{col}" stroke-width="{sw:.1f}"/>')
    if kind == "lamp":
        ly = top + 0.58 * h
        parts.append(f'<path d="M{x:.1f} {ly:.1f}Q{x - 16 * s:.1f} {ly - 20 * s:.1f} {x - 36 * s:.1f} {ly - 12 * s:.1f}" fill="none" stroke="{col}" stroke-width="{max(.9, 1.8 * s):.1f}"/>'
                     f'<path d="M{x - 44 * s:.1f} {ly - 12 * s:.1f}L{x - 28 * s:.1f} {ly - 14 * s:.1f}L{x - 31 * s:.1f} {ly - 7 * s:.1f}L{x - 41 * s:.1f} {ly - 6 * s:.1f}Z" fill="{col}"/>')
    g = f'<g opacity="{fade:.2f}">{"".join(parts)}</g>'
    return g, attach, (x, top - 8 * s, max(1.6, 2.4 * s))


# ---------------------------------------------------------------- streaks
LAYERS = [  # (length px, width, opacity, mix-with-white)
    (60, 8.0, 0.20, 0.0),    # glow
    (160, 1.2, 0.20, 0.0),   # long faint tail
    (92, 1.8, 0.45, 0.0),
    (42, 2.4, 0.95, 0.0),
    (12, 2.8, 1.00, 0.40),   # bright head
]


def streak(geom_id, chain_len, color, mode, D, phi, scale=1.0, frozen=None, ambient=False):
    """One light moving along the wire `geom_id`. frozen: fraction 0..1 of the trip for a still frame."""
    travel = chain_len + TAIL_MAX
    out = []
    for ln, w, op, white in LAYERS:
        ln = ln * scale
        col = mix(color, "#ffffff", white) if mode == "dark" else mix(color, "#000000", 0.12 * white)
        if mode == "light" and ln == 44 * scale:
            op *= 0.6
        if ambient:
            op *= 0.45
        off0 = ln
        attrs = (f'stroke="{col}" stroke-width="{w * (1 if scale >= 1 else .8):.1f}" stroke-opacity="{op:.2f}" '
                 f'stroke-linecap="round" fill="none" stroke-dasharray="{ln:.0f} {travel * 2:.0f}"')
        if frozen is not None:
            off = ln - frozen * travel
            out.append(f'<use href="#{geom_id}" xlink:href="#{geom_id}" {attrs} stroke-dashoffset="{off:.1f}"/>')
        else:
            out.append(f'<use href="#{geom_id}" xlink:href="#{geom_id}" {attrs} stroke-dashoffset="{off0:.1f}">'
                       f'<animate attributeName="stroke-dashoffset" values="{off0:.1f};{off0 - travel:.1f}" dur="{D}s" '
                       f'begin="{-phi * D:.2f}s" repeatCount="indefinite"/></use>')
    return "".join(out)


def chain_point(chain, dist):
    """Point at `dist` px along the wire (clamped)."""
    dist = max(0.0, min(chain.length, dist))
    for p, c, q in chain.segs:
        ln = _seg_len(p, c, q)
        if dist <= ln or (p, c, q) == chain.segs[-1]:
            t = min(1.0, dist / ln) if ln else 0
            u = 1 - t
            return (u * u * p[0] + 2 * u * t * c[0] + t * t * q[0], u * u * p[1] + 2 * u * t * c[1] + t * t * q[1])
        dist -= ln


def glint(geom_id, chain, color, mode, D, phi, size=1.0, frozen=None):
    """A small four-point spark riding at the head of a streak, like the flares in the reference image."""
    travel = chain.length + TAIL_MAX
    col = mix(color, "#ffffff", 0.7) if mode == "dark" else mix(color, "#000000", 0.1)
    r = 4.2 * size
    shape = (f'<path d="M{-r:.1f} 0H{r:.1f}M0 {-r:.1f}V{r:.1f}" stroke="{col}" stroke-width="1" stroke-linecap="round"/>'
             f'<circle r="{1.3 * size:.1f}" fill="{col}"/>')
    if frozen is not None:
        h = frozen * travel
        if h > chain.length:
            return ""
        x, y = chain_point(chain, h)
        return f'<g transform="translate({x:.1f} {y:.1f})" opacity=".95">{shape}</g>'
    k = chain.length / travel
    return (f'<g opacity="0">{shape}'
            f'<animateMotion dur="{D}s" begin="{-phi * D:.2f}s" repeatCount="indefinite" rotate="0" '
            f'keyPoints="0;1;1" keyTimes="0;{k:.4f};1" calcMode="linear"><mpath href="#{geom_id}" xlink:href="#{geom_id}"/></animateMotion>'
            f'<animate attributeName="opacity" values="0;.95;.95;0;0" keyTimes="0;.04;{max(k - .04, .05):.4f};{k:.4f};1" dur="{D}s" begin="{-phi * D:.2f}s" repeatCount="indefinite"/></g>')
