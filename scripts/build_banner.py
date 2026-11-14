"""Banner: transparent background, dark and light variants, animated or static.

Wires are neutral. Pulses are the information: one per active day and language, coloured by language.
Rings are events from other people (stars, forks, issues, PRs). Two grey pulses always travel
so the banner is never still, even before there is any data.
"""
import hashlib
import math

from common import MONO, esc, lang_color, lane_point, signal, theme

W, H = 1000, 300
BASE = 252
POLES = [(700, 46), (796, 72), (874, 94), (934, 112), (982, 126)]
MAX_PULSES = 16
MAX_RINGS = 6
NAME = "FreemanKlay"
LABEL = "SOFTWARE · GAME DEVELOPMENT · CREATIVE TECHNOLOGY"
SUBTITLE = "INDEPENDENT DEVELOPER"
TAGLINE = "I turn ideas into things that run."
STATUS = "AVAILABLE FOR PROJECTS"
ALT = f"{NAME}, Independent Developer. {TAGLINE}"


def _bars(i, x, t):
    s = 1 - 0.13 * i
    return [((x - 40 * s, t), (x + 40 * s, t)), ((x - 30 * s, t + 18 * s), (x + 30 * s, t + 18 * s))]


def lanes():
    """Four wire lanes, each a chain of quadratic segments from off-canvas left to off-canvas right."""
    bars = [_bars(i, x, t) for i, (x, t) in enumerate(POLES)]
    out = []
    for lane in range(4):
        b, side = lane // 2, lane % 2
        pts = [(-20, bars[0][b][side][1] - 10 + b * 8)]
        pts += [bars[i][b][side] for i in range(len(POLES))]
        pts += [(W + 20, pts[-1][1] + 6)]
        segs = []
        for k in range(len(pts) - 1):
            p, q = pts[k], pts[k + 1]
            dx = q[0] - p[0]
            sag = 34 if k == 0 else max(3, dx * 0.14)
            segs.append((p, ((p[0] + q[0]) / 2, (p[1] + q[1]) / 2 + sag), q))
        out.append(segs)
    return out, bars


def _path(segs):
    d = "M%.1f %.1f" % segs[0][0]
    for _, c, q in segs:
        d += "Q%.1f %.1f %.1f %.1f" % (c + q)
    return d


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


def build_banner(mode, data, static=False):
    T = theme(mode)
    green = signal(mode)
    segs_by_lane, bars = lanes()
    paths = [_path(s) for s in segs_by_lane]
    anim = not static

    defs = [
        '<linearGradient id="wf" x1="0" x2="1"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".57" stop-color="#fff" stop-opacity="0"/><stop offset=".72" stop-color="#fff"/></linearGradient>',
        f'<mask id="wm"><rect width="{W}" height="{H}" fill="url(#wf)"/></mask>',
        f'<clipPath id="tg"><rect x="40" y="200" width="{0 if anim else 620}" height="44">'
        + ('<animate attributeName="width" values="0;620" keyTimes="0;1" dur="2.4s" begin="0.3s" fill="freeze"/>' if anim else "")
        + "</rect></clipPath>",
        f'<clipPath id="fr"><rect width="{W}" height="{H}"/></clipPath>',
    ]

    scene = []
    for i, (x, t) in enumerate(POLES):
        w = max(1.2, 3.6 - 0.5 * i)
        scene.append(f'<path d="M{x} {t - 6}V{BASE}" stroke="{T["pole"]}" stroke-width="{w:.1f}"/>')
        for a, b in bars[i]:
            scene.append(f'<path d="M{a[0]:.0f} {a[1]:.0f}H{b[0]:.0f}" stroke="{T["pole"]}" stroke-width="{max(1.0, w * .65):.1f}"/>')
    scene.append(f'<path d="M430 {BASE}H{W}" stroke="{T["wire"]}" stroke-width="1" opacity=".5"/>')
    for k, d in enumerate(paths):
        scene.append(f'<path id="lane{k}" d="{d}" fill="none" stroke="{T["wire"]}" stroke-width="1.2"/>')

    moving = []

    def pulse(kind, lane, color, r, key, dur=None, op=1.0):
        h = _h(*key)
        if static:
            f = 0.5 + (h % 1000) / 1000 * 0.47
            x, y = lane_point(segs_by_lane[lane], f)
            if kind == "ring":
                return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="none" stroke="{color}" stroke-width="1.5"/>'
            return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{color}"/>'
        d = dur or 6 + h % 5
        begin = -(h % int(d * 10)) / 10
        shape = (f'<circle r="{r}" fill="none" stroke="{color}" stroke-width="1.5" opacity="0">' if kind == "ring"
                 else f'<circle r="{r}" fill="{color}" opacity="0">')
        return (shape
                + f'<animateMotion dur="{d}s" begin="{begin}s" repeatCount="indefinite" rotate="0"><mpath href="#lane{lane}" xlink:href="#lane{lane}"/></animateMotion>'
                + f'<animate attributeName="opacity" values="0;{op};{op};0" keyTimes="0;.06;.94;1" dur="{d}s" begin="{begin}s" repeatCount="indefinite"/></circle>')

    for i, (date, lang, commits) in enumerate(select_pulses(data)):
        r = round(2.4 + min(2.2, math.log2(commits + 1) * 0.7), 1)
        moving.append(pulse("dot", i % 4, lang_color(lang, mode), r, (date, lang, i)))
    for i, e in enumerate(data.get("others", [])[:MAX_RINGS]):
        moving.append(pulse("ring", (i * 3 + 1) % 4, T["text"], 3.8, (e["date"], e["kind"], i), op=0.9))
    if anim:  # two grey carriers, always moving, clearly not data
        moving.append(pulse("dot", 1, T["ambient"], 2, ("ambient", 1), dur=12, op=0.55))
        moving.append(pulse("dot", 2, T["ambient"], 2, ("ambient", 2), dur=15, op=0.55))

    def name_copy(color, values, ops):
        keys = "0;0.80;0.81;0.83;0.84;0.86;1"
        return (f'<g opacity="0"><animate attributeName="opacity" values="{ops}" keyTimes="{keys}" dur="7s" repeatCount="indefinite"/>'
                f'<animateTransform attributeName="transform" type="translate" values="{values}" keyTimes="{keys}" dur="7s" repeatCount="indefinite"/>'
                f'<text x="46" y="146" font-family="{MONO}" font-size="84" font-weight="700" letter-spacing="-3" fill="{color}">{NAME}</text></g>')

    ghosts = ""
    if anim:
        ghosts = (name_copy(T["ghost_a"], "0 0;0 0;-5 1;4 -1;-3 0;0 0;0 0", "0;0;.75;0;.55;0;0")
                  + name_copy(T["ghost_b"], "0 0;0 0;5 -1;-4 1;3 0;0 0;0 0", "0;0;.75;0;.55;0;0"))
    dot_anim = '<animate attributeName="opacity" values="1;.3;1" dur="2.4s" repeatCount="indefinite"/>' if anim else ""

    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(ALT)}">
<title>{esc(ALT)}</title>
<defs>{"".join(defs)}</defs>
<g clip-path="url(#fr)">
<g mask="url(#wm)">{"".join(scene)}{"".join(moving)}</g>
<text x="48" y="62" font-family="{MONO}" font-size="15" letter-spacing="1.5" fill="{T["muted"]}">{LABEL}</text>
{ghosts}
<text x="46" y="146" font-family="{MONO}" font-size="84" font-weight="700" letter-spacing="-3" fill="{T["text"]}">{NAME}</text>
<text x="50" y="184" font-family="{MONO}" font-size="20" letter-spacing="6" fill="{T["muted"]}">{SUBTITLE}</text>
<g clip-path="url(#tg)"><text x="48" y="228" font-family="{MONO}" font-size="28" fill="{T["text"]}">{TAGLINE}</text></g>
<circle cx="53" cy="270" r="6" fill="{green}">{dot_anim}</circle>
<text x="72" y="276" font-family="{MONO}" font-size="17" letter-spacing="3" fill="{T["muted"]}">{STATUS}</text>
</g>
</svg>'''
