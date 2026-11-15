"""The wire scenes: the banner's poles and the corner piece, both driven by the same activity data.

Each pulse of activity becomes a light travelling along a wire, coloured by its language. The corner
piece reuses the first pulses of the banner with the same colour, trip time and phase, so the two
pieces move together. Variants: "anim" (SMIL), "still" (frozen frame) and "both" (one SVG that hides
the motion for people who ask their system to reduce it).
"""
import hashlib
import math

from common import lang_color, theme
from scene import Chain, glint, pole, streak, wire_chain

MAX_PULSES = 16
MAX_RINGS = 6
CORNER_PULSES = 8
CORNER_RINGS = 2
NS = 'xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink"'
STOPS_BANNER = '<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".60" stop-color="#fff" stop-opacity="0"/><stop offset=".70" stop-color="#fff"/>'
STOPS_CORNER = '<stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".22" stop-color="#fff"/>'
STYLE = '<style>.still{display:none}@media (prefers-reduced-motion:reduce){.anim{display:none}.still{display:inline}}</style>'


def _h(*parts):
    return int(hashlib.sha1("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def select_pulses(data):
    items = [p for p in data.get("pulses", []) if p["commits"] > 0]
    if len(items) <= MAX_PULSES:
        return [(p["date"], p["language"], p["commits"]) for p in items]
    totals = {}
    for p in items:
        totals[p["language"]] = totals.get(p["language"], 0) + p["commits"]
    grand = sum(totals.values())
    raw = {k: v * MAX_PULSES / grand for k, v in totals.items()}
    counts = {k: int(v) for k, v in raw.items()}
    left = MAX_PULSES - sum(counts.values())
    for k in sorted(raw, key=lambda k: -(raw[k] - counts[k]))[:left]:
        counts[k] += 1
    out = []
    for lang, n in counts.items():
        share = totals[lang] / max(n, 1)
        out += [("mix%d" % i, lang, max(1, round(share))) for i in range(n)]
    return out


def make_specs(data, mode, lanes, pulses=MAX_PULSES, rings=MAX_RINGS, ambient=2):
    """One streak per pulse. D is 5 or 10 s. Hash-based, so the banner and the corner agree."""
    specs = []
    for i, (date, lang, commits) in enumerate(select_pulses(data)[:pulses]):
        h = _h(date, lang, i)
        specs.append(dict(lane=h % lanes, color=lang_color(lang, mode), D=(5, 10)[h % 2], phi=(h % 997) / 997,
                          still=0.30 + 0.5 * ((h >> 8) % 1000) / 1000, scale=1.0, size=min(1.4, 0.9 + 0.12 * math.log2(commits + 1))))
    for i, e in enumerate(data.get("others", [])[:rings]):
        h = _h(e["date"], e["kind"], i)
        specs.append(dict(lane=(h + 2) % lanes, color=theme(mode)["text"], D=(5, 10)[h % 2], phi=(h % 991) / 991,
                          still=0.30 + 0.5 * ((h >> 8) % 1000) / 1000, scale=0.6, size=0.8, other=True))
    for i in range(ambient):
        h = _h("ambient", i)
        specs.append(dict(lane=(i * 3 + 1) % lanes, color=theme(mode)["ambient"], D=10, phi=(h % 983) / 983,
                          scale=1.0, ambient=True))
    return specs


def _light(specs, chains, mode, kind):
    out = []
    for sp in specs:
        if kind == "still" and sp.get("ambient"):
            continue
        ch = chains[sp["lane"]]
        gid = f"g{sp['lane']}"
        frozen = sp["still"] if kind == "still" else None
        out.append(streak(gid, ch.length, sp["color"], mode, sp["D"], sp["phi"], sp.get("scale", 1.0), frozen=frozen,
                          ambient=sp.get("ambient", False)))
        if not sp.get("ambient") and not sp.get("other"):
            out.append(glint(gid, ch, sp["color"], mode, sp["D"], sp["phi"], size=sp.get("size", 1.0), frozen=frozen))
    return "".join(out)


def _compose(mode, chains, poles_svg, specs, variant, mask_id, stops, W, H, extra_common="", extra_anim="", extra_still=""):
    T = theme(mode)
    defs = "".join(f'<path id="g{j}" d="{c.d()}" fill="none"/>' for j, c in enumerate(chains))
    defs += (f'<linearGradient id="{mask_id}g" x1="0" x2="1">{stops}</linearGradient>'
             f'<mask id="{mask_id}"><rect width="{W}" height="{H}" fill="url(#{mask_id}g)"/></mask>')
    wires = "".join(f'<use href="#g{j}" xlink:href="#g{j}" stroke="{T["wire"]}" stroke-width="1.1" opacity=".9" fill="none"/>'
                    for j in range(len(chains)))
    if variant == "anim":
        light = _light(specs, chains, mode, "anim") + extra_anim
    elif variant == "still":
        light = _light(specs, chains, mode, "still") + extra_still
    else:
        light = (f'<g class="anim">{_light(specs, chains, mode, "anim")}{extra_anim}</g>'
                 f'<g class="still">{_light(specs, chains, mode, "still")}{extra_still}</g>')
    return defs, f'<g mask="url(#{mask_id})">{poles_svg}{wires}{extra_common}{light}</g>'


def banner_scene(mode, data, variant, W=1000, H=300):
    S = [1.0, 0.82, 0.68, 0.57, 0.48]
    xs = [700, 790, 865, 927, 975]
    kinds = ["lamp", "plain", "transformer", "plain", "tower"]
    polesvg, attach, beacon = [], [], None
    for k in range(5):
        s = S[k]
        g, a, b = pole(xs[k], 170 + 82 * s, 206 * s, mode, kinds[k], fade=0.6 + 0.4 * s)
        polesvg.append(g)
        attach.append(a)
        if kinds[k] == "tower":
            beacon = b
    chains = []
    for j in range(6):
        pts = [attach[k][j] for k in range(5)]
        chains.append(wire_chain(pts, lead_in=(430, pts[0][1] + 10 + 2 * j), tail=(1030, pts[-1][1] + 4), sag_k=0.085, lane=j))
    T = theme(mode)
    slack = "".join(f'<path d="{c.d()}" fill="none" stroke="{T["wire"]}" stroke-width=".8" opacity=".55"/>'
                    for c in (Chain([attach[0][1], attach[2][4]], [34]), Chain([attach[1][3], attach[3][5]], [22])))
    bx, by, br = beacon
    dot = f'<circle cx="{bx:.1f}" cy="{by:.1f}" r="{br:.1f}" fill="{T["ghost_a"]}"'
    blink = dot + '><animate attributeName="opacity" values="1;.15;1" dur="2.4s" repeatCount="indefinite"/></circle>'
    return _compose(mode, chains, "".join(polesvg), make_specs(data, mode, 6), variant, "wm2", STOPS_BANNER, W, H,
                    extra_common=slack, extra_anim=blink, extra_still=dot + "/>")


def corner_scene(mode, data, variant, W=400, H=200):
    """One close pole with a transformer at the right edge; the wires sweep away to the left."""
    g, a, _ = pole(338, 214, 196, mode, "transformer", fade=1.0)
    chains = []
    for j in range(6):
        p = a[j]
        chains.append(Chain([(-20, 126 + 9 * j), p, (W + 20, p[1] + 10 + 2 * j)], [38 + 8 * j, 5]))
    specs = make_specs(data, mode, 6, pulses=CORNER_PULSES, rings=CORNER_RINGS, ambient=1)
    return _compose(mode, chains, g, specs, variant, "mc", STOPS_CORNER, W, H)


def build_corner(mode, data, static=False, adaptive=True):
    variant = "still" if static else ("both" if adaptive else "anim")
    defs, body = corner_scene(mode, data, variant)
    style = STYLE if variant == "both" else ""
    return (f'<svg {NS} viewBox="0 0 400 200" width="400" height="200" aria-hidden="true" focusable="false">{style}'
            f'<defs>{defs}</defs>{body}</svg>')
