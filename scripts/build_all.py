"""Builds every generated SVG: banner (4), languages card (2), section labels, chips and tool tiles."""
import argparse
import json
from pathlib import Path

from build_banner import build_banner
from build_languages import build_languages
import build_sections as S
from common import PALETTE
import re, unicodedata


def slug(text):
    t = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower().replace("+", "p")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")


SPEAKS = ["English", "Español", "Português"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    data = {}
    if a.data and Path(a.data).exists():
        data = json.loads(Path(a.data).read_text(encoding="utf-8"))
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for mode in ("dark", "light"):
        (out / f"banner-{mode}.svg").write_text(build_banner(mode, data), encoding="utf-8")
        (out / f"banner-{mode}-static.svg").write_text(build_banner(mode, data, static=True), encoding="utf-8")
        (out / f"languages-{mode}.svg").write_text(build_languages(mode, data.get("languages", [])), encoding="utf-8")
        for label in ("STACK", "TOOLS", "SPEAKS"):
            (out / f"label-{label.lower()}-{mode}.svg").write_text(S.section_label(label, mode), encoding="utf-8")
        for name in PALETTE["order"]:
            (out / f"chip-{slug(name)}-{mode}.svg").write_text(S.lang_chip(name, mode), encoding="utf-8")
        for i in range(3):
            (out / f"tools-{i + 1}-{mode}.svg").write_text(S.tools_tile(i, mode), encoding="utf-8")
        for t in SPEAKS:
            (out / f"speak-{slug(t)}-{mode}.svg").write_text(S.plain_chip(t, mode), encoding="utf-8")
    print("built", len(list(out.glob("*.svg"))), "SVGs in", out)


if __name__ == "__main__":
    main()
