"""Section pieces: labels, language chips, tool tiles, simple chips.

Every piece is its own transparent SVG with a fixed width, so on a phone the pieces wrap onto new
lines by themselves instead of shrinking their text. Text is centred on its row with dy=".35em"
so icon and text line up whatever font the viewer's browser picks.
"""
import json
from pathlib import Path

from common import MONO, SANS, esc, for_light, lang_color, mix, theme

ICONS = json.loads((Path(__file__).resolve().parent / "icons.json").read_text(encoding="utf-8"))
TILE_W = 270

# (group, items). The grouping says it all; no extra badge for the creative tools.
TOOLS = [
    ("Development & Engineering", ["Visual Studio Code", "Git", "Docker"]),
    ("Game Development", ["Unreal Engine"]),
    ("Creative Software", ["Photoshop", "Premiere Pro", "FL Studio"]),
]

# tool icons: the brand colour, pulled toward the nearest colour of our palette
# name: (brand colour, palette colour, how far to pull)
TOOL_COLORS = {
    "Visual Studio Code": ("#2f9de4", "#8fa3d9", 0.55),
    "Git": ("#f05032", "#e58f9c", 0.55),
    "Docker": ("#2496ed", "#8fa3d9", 0.45),
    "Unreal Engine": ("#e6edf3", "#d5ded2", 0.60),
    "Photoshop": ("#31a8ff", "#8fa3d9", 0.60),
    "Premiere Pro": ("#9999ff", "#8fa3d9", 0.50),
    "FL Studio": ("#f4932b", "#e0b469", 0.60),
}


def tool_color(name, mode):
    brand, target, t = TOOL_COLORS[name]
    c = mix(brand, target, t)
    return c if mode == "dark" else for_light(c)


def optical_scale(ic):
    """Glyphs that fill their box (square logos) look bigger than open ones, so they get a little less room."""
    cover = ic.get("cover", 0.5)
    if cover >= 0.78:
        return 0.84
    if cover >= 0.55:
        return 0.94
    if cover < 0.3:  # thin, open glyphs (Java, Unreal) read small at chip size
        return 1.1
    return 1.0


def _wrap(w, h, body, label):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="{esc(label)}">'
            f'<title>{esc(label)}</title>{body}</svg>')


def icon(key, x, y, size, color):
    """Draws the glyph centred in a size x size cell, every glyph fitted by its real bounds."""
    ic = ICONS[key]
    bx, by, side = ic["box"]
    s = size * optical_scale(ic)
    off = (size - s) / 2
    return (f'<svg x="{x + off:.2f}" y="{y + off:.2f}" width="{s:.2f}" height="{s:.2f}" '
            f'viewBox="{bx} {by} {side} {side}" fill="{color}">{ic["body"]}</svg>')


def section_label(text, mode, width=640):
    T = theme(mode)
    lw = len(text) * 10.8
    body = (f'<text x="0" y="18" dy=".35em" font-family="{MONO}" font-size="13" letter-spacing="3" fill="{T["muted"]}">{esc(text)}</text>'
            f'<path d="M{lw + 16:.0f} 18.5H{width}" stroke="{T["border"]}" stroke-width="1"/>')
    return _wrap(width, 36, body, text.title())


def lang_chip(name, mode):
    T = theme(mode)
    color = lang_color(name, mode)
    w = 40 + len(name) * 8.6 + 16
    body = f'<rect x=".5" y=".5" width="{w:.1f}" height="35" rx="8" fill="none" stroke="{T["border"]}"/>'
    body += icon(name, 11, 9, 18, color)
    body += f'<text x="38" y="18" dy=".35em" font-family="{MONO}" font-size="14" fill="{T["text"]}">{esc(name)}</text>'
    return _wrap(round(w + 1), 36, body, name)


def plain_chip(text, mode):
    T = theme(mode)
    w = 32 + len(text) * 8.6
    body = (f'<rect x=".5" y=".5" width="{w:.1f}" height="35" rx="8" fill="none" stroke="{T["border"]}"/>'
            f'<text x="16" y="18" dy=".35em" font-family="{MONO}" font-size="14" fill="{T["text"]}">{esc(text)}</text>')
    return _wrap(round(w + 1), 36, body, text)


ROW_TOP, ROW_PITCH, ICON_CELL = 58, 42, 26


def tools_tile(i, mode):
    """Same header line and same row grid in every group, so the three columns line up."""
    T = theme(mode)
    name, items = TOOLS[i]
    body = f'<path d="M0 .5H{TILE_W}" stroke="{T["border"]}"/>'
    body += f'<text x="0" y="30" dy=".35em" font-family="{SANS}" font-size="17" font-weight="600" fill="{T["text"]}">{esc(name)}</text>'
    for k, it in enumerate(items):
        top = ROW_TOP + k * ROW_PITCH
        mid = top + ICON_CELL / 2
        body += icon(it, 0, top, ICON_CELL, tool_color(it, mode))
        body += f'<text x="40" y="{mid}" dy=".35em" font-family="{SANS}" font-size="16" fill="{T["text"]}">{esc(it)}</text>'
    label = name + ": " + ", ".join(items)
    return _wrap(TILE_W, ROW_TOP + ROW_PITCH * 3 - 14, body, label)
