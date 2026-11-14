"""Moves the cool-readme cards (summary ring, weekly bars) onto our green.

The tool only offers preset colours, so after it draws its cards we swap its greens for ours.
If the tool changes its colours this step simply finds nothing to swap.
"""
import re
import sys
from pathlib import Path

from common import mix, signal

# the tool's greens, from its source (src/render/svg.ts)
DARK = {"#39d353": 1.0, "#26a641": 0.75, "#006d32": 0.45, "#0e4429": 0.22, "#3fb950": 1.0}
LIGHT = {"#216e39": 1.0, "#30a14e": 0.75, "#40c463": 0.5, "#9be9a8": 0.28, "#2da44e": 1.0}


def mapping(mode):
    green = signal(mode)
    base = "#0d1117" if mode == "dark" else "#ffffff"
    table = DARK if mode == "dark" else LIGHT
    return {k: mix(base, green, t) for k, t in table.items()}


def recolor(text, mode):
    for old, new in mapping(mode).items():
        text = re.sub(re.escape(old), new, text, flags=re.I)
    return text


def main():
    folder = Path(sys.argv[1])
    n = 0
    for f in folder.glob("*.svg"):
        if not f.name.startswith(("summary-", "weekly-")):
            continue
        mode = "dark" if f.stem.endswith("-dark") else "light"
        old = f.read_text(encoding="utf-8")
        new = recolor(old, mode)
        if new != old:
            f.write_text(new, encoding="utf-8")
            n += 1
    print(f"recoloured {n} card(s)")


if __name__ == "__main__":
    main()
