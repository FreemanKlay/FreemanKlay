"""Builds every generated SVG: banner (4), languages card (2), stack pills (2)."""
import argparse
import json
from pathlib import Path

from build_banner import build_banner
from build_languages import build_languages, build_stack


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
        (out / f"stack-{mode}.svg").write_text(build_stack(mode), encoding="utf-8")
    print("built 8 SVGs in", out)


if __name__ == "__main__":
    main()
