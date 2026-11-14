"""Shared helpers: palette, light/dark themes, colour maths, small geometry."""
import colorsys
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PALETTE = json.loads((ROOT / "palette.json").read_text(encoding="utf-8"))

MONO = "ui-monospace,SFMono-Regular,'JetBrains Mono',Menlo,Consolas,monospace"
SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI','Noto Sans',Helvetica,Arial,sans-serif"


def hex_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb_hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, round(c))) for c in rgb)


def _lin(c):
    c /= 255
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def luminance(h):
    r, g, b = hex_rgb(h)
    return 0.2126 * _lin(r) + 0.7152 * _lin(g) + 0.0722 * _lin(b)


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def mix(a, b, t):
    ra, rb = hex_rgb(a), hex_rgb(b)
    return rgb_hex([ra[i] + (rb[i] - ra[i]) * t for i in range(3)])


def for_light(color, bg="#ffffff", target=3.0):
    """Darken a dark-theme colour, keeping its hue, until it reads on a light page."""
    r, g, b = [c / 255 for c in hex_rgb(color)]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    s = min(1.0, s * 1.15)
    cand = color
    while l > 0.05:
        cand = rgb_hex([c * 255 for c in colorsys.hls_to_rgb(h, l, s)])
        if contrast(cand, bg) >= target:
            return cand
        l -= 0.01
    return cand


def lang_color(name, mode):
    base = PALETTE["languages"].get(name, PALETTE["other"])
    return base if mode == "dark" else for_light(base)


def signal(mode):
    base = PALETTE["signal"]
    return base if mode == "dark" else for_light(base)


def theme(mode):
    if mode == "dark":
        return dict(text="#e6edf3", muted="#8b949e", wire="#4b5360", pole="#4b5360",
                    ambient="#7d8590", scan="#ffffff", scan_op=0.035, band_op=0.06,
                    ghost_a="#e58f9c", ghost_b="#8fa3d9", border="#3d444d", track="#30363d")
    return dict(text="#1f2328", muted="#59636e", wire="#a3abb4", pole="#8c959f",
                ambient="#8c959f", scan="#000000", scan_op=0.03, band_op=0.045,
                ghost_a=for_light("#e58f9c"), ghost_b=for_light("#8fa3d9"),
                border="#d1d9e0", track="#d8dee4")


def percentages(items, top=5, max_items=6):
    """items: [{'name','bytes'}] -> [(name, pct int)] summing to 100, 'Other' if there are many."""
    items = sorted((i for i in items if i["bytes"] > 0), key=lambda i: -i["bytes"])
    if not items:
        return []
    if len(items) > max_items:
        rest = sum(i["bytes"] for i in items[top:])
        items = items[:top] + [{"name": "Other", "bytes": rest}]
    total = sum(i["bytes"] for i in items)
    raw = [i["bytes"] * 100 / total for i in items]
    floors = [int(x) for x in raw]
    left = 100 - sum(floors)
    order = sorted(range(len(raw)), key=lambda k: -(raw[k] - floors[k]))
    for k in order[:left]:
        floors[k] += 1
    return [(i["name"], p) for i, p in zip(items, floors)]


def bezier_point(p, c, q, t):
    u = 1 - t
    return (u * u * p[0] + 2 * u * t * c[0] + t * t * q[0],
            u * u * p[1] + 2 * u * t * c[1] + t * t * q[1])


def lane_point(segs, f):
    """Point at fraction f (0..1) along a chain of quadratic segments [(p, c, q), ...]."""
    lengths = [math.dist(p, q) for p, _, q in segs]
    target = f * sum(lengths)
    for (p, c, q), ln in zip(segs, lengths):
        if target <= ln or (p, c, q) == segs[-1]:
            return bezier_point(p, c, q, min(1.0, target / ln if ln else 0))
        target -= ln


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")
