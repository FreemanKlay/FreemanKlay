"""Banner: transparent background, dark and light variants, animated or static.

Wires are neutral. The light travelling along them is the information: one light per active day and
language, coloured by language; white lights for events from other people (stars, forks, issues, PRs).
Two faint grey lights always travel, so the banner is never still, even before there is any data.
The scene itself (poles, wires, lights) lives in scenes.py.
"""
from common import PALETTE, MONO, esc, for_light, signal, theme
from scenes import banner_scene, select_pulses  # noqa: F401  (select_pulses re-exported)

PALETTE_SIGNAL = PALETTE["signal"]
W, H = 1000, 300
NAME = "Freeman Klay"
LABEL = "SOFTWARE · GAME DEVELOPMENT · CREATIVE TECHNOLOGY"
SUBTITLE = "INDEPENDENT DEVELOPER"
TAGLINE = "Creating possibilities."
STATUS = "AVAILABLE FOR PROJECTS"
ALT = f"{NAME}, Independent Developer. {TAGLINE}"


STYLE = '<style>.still{display:none}@media (prefers-reduced-motion:reduce){.anim{display:none}.still{display:inline}}</style>'


def build_banner(mode, data, static=False, adaptive=False):
    """static: no motion at all. adaptive: both, and the SVG itself hides the motion for people who ask
    their system to reduce it (one file per theme, no extra <source> rules in the README)."""
    T = theme(mode)
    green = signal(mode)
    anim = not static
    variant = "both" if adaptive else ("still" if static else "anim")
    sdefs, sbody = banner_scene(mode, data, variant)

    defs = [
        sdefs,
        f'<clipPath id="tg"><rect x="40" y="200" width="{0 if anim else 620}" height="44">'
        + ('<animate attributeName="width" values="0;620" keyTimes="0;1" dur="2.4s" begin="0.3s" fill="freeze"/>' if anim else "")
        + "</rect></clipPath>",
        f'<clipPath id="fr"><rect width="{W}" height="{H}"/></clipPath>',
    ]

    def name_copy(color, values, ops):
        keys = "0;0.80;0.81;0.83;0.84;0.86;1"
        return (f'<g opacity="0"><animate attributeName="opacity" values="{ops}" keyTimes="{keys}" dur="7s" repeatCount="indefinite"/>'
                f'<animateTransform attributeName="transform" type="translate" values="{values}" keyTimes="{keys}" dur="7s" repeatCount="indefinite"/>'
                f'<text x="46" y="146" font-family="{MONO}" font-size="84" font-weight="700" letter-spacing="-3" fill="{color}">{NAME}</text></g>')

    ghosts = ""
    if anim:
        ghosts = (name_copy(T["ghost_a"], "0 0;0 0;-5 1;4 -1;-3 0;0 0;0 0", "0;0;.75;0;.55;0;0")
                  + name_copy(T["ghost_b"], "0 0;0 0;5 -1;-4 1;3 0;0 0;0 0", "0;0;.75;0;.55;0;0"))
        if adaptive:
            ghosts = f'<g class="anim">{ghosts}</g>'

    pill_text = green if mode == "dark" else for_light(PALETTE_SIGNAL, target=4.5)
    pw = 40 + len(STATUS) * 10.6
    glow_rect = (f'<rect x="48" y="252" width="{pw:.0f}" height="36" rx="18" fill="none" stroke="{green}" stroke-opacity=".3">'
                 '<animate attributeName="stroke-opacity" values=".0;.35;.0" dur="3.2s" repeatCount="indefinite"/></rect>')
    glow = f'<g class="anim">{glow_rect}</g>' if adaptive else (glow_rect if anim else "")
    pill = (f'<rect x="48" y="252" width="{pw:.0f}" height="36" rx="18" fill="{green}" fill-opacity="{0.14 if mode == "dark" else 0.12}" '
            f'stroke="{green}" stroke-opacity=".5"/>{glow}'
            f'<text x="{48 + pw / 2:.0f}" y="270" dy=".35em" text-anchor="middle" font-family="{MONO}" font-size="15" font-weight="700" '
            f'letter-spacing="1.6" fill="{pill_text}">{STATUS}</text>')

    tag_text = f'<text x="48" y="228" font-family="{MONO}" font-size="28" fill="{T["text"]}">{TAGLINE}</text>'
    if adaptive:
        tagline = f'<g class="anim" clip-path="url(#tg)">{tag_text}</g><g class="still">{tag_text}</g>'
    elif anim:
        tagline = f'<g clip-path="url(#tg)">{tag_text}</g>'
    else:
        tagline = tag_text
    style = STYLE if adaptive else ""

    return f'''<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-label="{esc(ALT)}">
<title>{esc(ALT)}</title>{style}
<defs>{"".join(defs)}</defs>
<g clip-path="url(#fr)">
{sbody}
<text x="48" y="62" font-family="{MONO}" font-size="15" letter-spacing="1.5" fill="{T["muted"]}">{LABEL}</text>
{ghosts}
<text x="46" y="146" font-family="{MONO}" font-size="84" font-weight="700" letter-spacing="-3" fill="{T["text"]}">{NAME}</text>
<text x="50" y="184" font-family="{MONO}" font-size="20" letter-spacing="6" fill="{T["muted"]}">{SUBTITLE}</text>
{tagline}
{pill}
</g>
</svg>'''
