"""Languages card (transparent, dark and light) and the stack pills that act as the colour legend."""
from common import MONO, PALETTE, SANS, esc, lang_color, percentages, theme

VW, VH = 480, 236


def build_languages(mode, languages):
    T = theme(mode)
    items = percentages(languages)
    x0, bw, by, bh, gap = 24, 432, 56, 16, 3
    parts = [f'<text x="24" y="34" font-family="{SANS}" font-size="13" font-weight="600" letter-spacing="2.2" fill="{T["muted"]}">MOST USED LANGUAGES</text>']
    if not items:
        parts.append(f'<rect x="{x0}" y="{by}" width="{bw}" height="{bh}" rx="8" fill="{T["track"]}" opacity=".6"/>')
        parts.append(f'<text x="24" y="118" font-family="{SANS}" font-size="15" fill="{T["muted"]}">No language data yet</text>')
        label = "Most used languages: no data yet"
    else:
        inner = bw - gap * (len(items) - 1)
        widths = [max(5.0, p * inner / 100) for _, p in items]
        scale = inner / sum(widths)
        widths = [w * scale for w in widths]
        x, segs = float(x0), []
        for (name, _), w in zip(items, widths):
            color = lang_color(name, mode) if name != "Other" else lang_color("Other", mode)
            segs.append(f'<rect x="{x:.2f}" y="{by}" width="{w:.2f}" height="{bh}" fill="{color}"/>')
            x += w + gap
        parts.append(f'<clipPath id="bar"><rect x="{x0}" y="{by}" width="{bw}" height="{bh}" rx="8"/></clipPath>')
        parts.append(f'<g clip-path="url(#bar)">{"".join(segs)}</g>')
        for i, (name, pct) in enumerate(items):
            cx = 24 + (i % 2) * 228
            cy = 116 + (i // 2) * 40
            color = lang_color(name, mode)
            parts.append(f'<circle cx="{cx + 7}" cy="{cy - 5}" r="6" fill="{color}"/>')
            parts.append(f'<text x="{cx + 22}" y="{cy}" font-family="{SANS}" font-size="16" fill="{T["text"]}">{esc(name)}</text>')
            parts.append(f'<text x="{cx + 196}" y="{cy}" text-anchor="end" font-family="{SANS}" font-size="15" fill="{T["muted"]}">{pct}%</text>')
        label = "Most used languages: " + ", ".join(f"{n} {p}%" for n, p in items)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {VW} {VH}" width="{VW}" height="{VH}" role="img" aria-label="{esc(label)}">'
            f'<title>{esc(label)}</title>{"".join(parts)}</svg>')


def build_stack(mode, max_width=740):
    T = theme(mode)
    names = PALETTE["order"]
    rows, row, x = [], [], 0
    for n in names:
        w = 18 + 10 + 8 + len(n) * 8.6 + 16
        if row and x + w > max_width:
            rows.append(row)
            row, x = [], 0
        row.append((n, x, w))
        x += w + 10
    rows.append(row)
    parts, total_w = [], 0
    for r, row in enumerate(rows):
        y = r * 46
        for n, x, w in row:
            total_w = max(total_w, x + w)
            parts.append(f'<rect x="{x + .5:.1f}" y="{y + .5}" width="{w:.1f}" height="35" rx="8" fill="none" stroke="{T["border"]}"/>'
                         f'<circle cx="{x + 18:.1f}" cy="{y + 18}" r="5" fill="{lang_color(n, mode)}"/>'
                         f'<text x="{x + 32:.1f}" y="{y + 23}" font-family="{MONO}" font-size="14" fill="{T["text"]}">{esc(n)}</text>')
    h = len(rows) * 46 - 10
    label = "Stack: " + ", ".join(names)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {total_w + 1:.0f} {h}" width="{total_w + 1:.0f}" height="{h}" role="img" aria-label="{esc(label)}">'
            f'<title>{esc(label)}</title>{"".join(parts)}</svg>')
