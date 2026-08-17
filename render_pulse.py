#!/usr/bin/env python3
"""
Render homelab pulse data into SVG cards + inject a block into README.md.

Input:  data/pulse.json  (written by n8n, committed via the GitHub contents API)
Output: assets/pulse-dark.svg, assets/pulse-light.svg, updated README.md

No third-party deps. Deliberately: fewer things to break in CI.
"""

from __future__ import annotations

import json
import pathlib
import re
import sys
from datetime import datetime, timezone

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "pulse.json"
README = ROOT / "README.md"
ASSETS = ROOT / "assets"

START = "<!-- pulse:start -->"
END = "<!-- pulse:end -->"

W, H = 840, 208

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "tile": "#161b22",
        "stroke": "#30363d",
        "text": "#e6edf3",
        "muted": "#8b949e",
        "accent": "#58a6ff",
        "bar": "#3fb950",
        "bar_dim": "#1f6f3f",
    },
    "light": {
        "bg": "#ffffff",
        "tile": "#f6f8fa",
        "stroke": "#d0d7de",
        "text": "#1f2328",
        "muted": "#59636e",
        "accent": "#0969da",
        "bar": "#1a7f37",
        "bar_dim": "#aceebb",
    },
}


def esc(s: object) -> str:
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def tile(x: int, y: int, w: int, h: int, label: str, value: str, sub: str, t: dict) -> str:
    return f"""
  <g>
    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8"
          fill="{t['tile']}" stroke="{t['stroke']}"/>
    <text x="{x + 14}" y="{y + 24}" font-size="11" font-weight="600"
          letter-spacing="0.8" fill="{t['muted']}">{esc(label.upper())}</text>
    <text x="{x + 14}" y="{y + 56}" font-size="26" font-weight="700"
          fill="{t['text']}">{esc(value)}</text>
    <text x="{x + 14}" y="{y + 76}" font-size="11" fill="{t['muted']}">{esc(sub)}</text>
  </g>"""


def sparkline(x: int, y: int, w: int, h: int, series: list, t: dict) -> str:
    if not series:
        return ""
    peak = max(series) or 1
    gap = 3
    bw = max(2.0, (w - gap * (len(series) - 1)) / len(series))
    out = []
    for i, v in enumerate(series):
        bh = max(2.0, (v / peak) * h)
        bx = x + i * (bw + gap)
        by = y + h - bh
        fill = t["bar"] if v == peak else t["bar_dim"]
        out.append(
            f'<rect x="{bx:.1f}" y="{by:.1f}" width="{bw:.1f}" height="{bh:.1f}" '
            f'rx="2" fill="{fill}"/>'
        )
    return "".join(out)


def card(d: dict, theme: str) -> str:
    t = THEMES[theme]
    stamp = d.get("generated_at", datetime.now(timezone.utc).isoformat(timespec="seconds"))
    hosts_up = d.get("hosts_up", 0)
    hosts_total = d.get("hosts_total", 0)
    ratio = (hosts_up / hosts_total) if hosts_total else 0
    health = t["bar"] if ratio == 1 else (t["accent"] if ratio >= 0.75 else "#d29922")

    tiles = [
        ("containers", d.get("containers_running", "-"), f"across {hosts_total} hosts"),
        ("library", d.get("library_size", "-"), f"{d.get('library_items', '-')} items"),
        ("streamed", d.get("watch_hours_7d", "-"), "hours, last 7 days"),
        ("automations", d.get("workflow_runs_7d", "-"), "n8n runs, last 7 days"),
    ]

    tw, th = 186, 92
    gap = 32
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" role="img" aria-label="Homelab pulse">',
        f'<rect width="{W}" height="{H}" rx="10" fill="{t["bg"]}" stroke="{t["stroke"]}"/>',
        '<defs><linearGradient id="banner" x1="0" y1="0" x2="1" y2="0">'
        '<stop offset="0" stop-color="#7c3aed"/><stop offset="0.55" stop-color="#2563eb"/>'
        '<stop offset="1" stop-color="#0891b2"/></linearGradient>'
        f'<clipPath id="top"><rect width="{W}" height="46" rx="10"/></clipPath></defs>',
        f'<rect width="{W}" height="46" fill="url(#banner)" clip-path="url(#top)"/>',
        '<text x="24" y="29" font-size="14" font-weight="700" letter-spacing="1.2" '
        'fill="#ffffff">HOMELAB PULSE</text>',
        f'<circle cx="{W - 168}" cy="24" r="4" fill="{health}"/>',
        f'<text x="{W - 156}" y="29" font-size="11" fill="#e9d5ff">'
        f'{hosts_up}/{hosts_total} hosts up</text>',
    ]

    for i, (label, value, sub) in enumerate(tiles):
        parts.append(tile(24 + i * (tw + 10), 66, tw, th, label, value, sub, t))

    parts.append(
        f'<text x="24" y="180" font-size="10" letter-spacing="0.8" '
        f'fill="{t["muted"]}">DAILY PLAY HOURS</text>'
    )
    parts.append(sparkline(150, 166, 400, 20, d.get("daily_hours", []), t))
    parts.append(
        f'<text x="{W - 24}" y="186" text-anchor="end" font-size="10" '
        f'fill="{t["muted"]}">updated {esc(stamp)}</text>'
    )
    parts.append("</svg>")

    svg = "\n".join(parts)
    # Font stack applied once on the root rather than per-node.
    return svg.replace(
        "<svg ",
        '<svg font-family="-apple-system,BlinkMacSystemFont,Segoe UI,Helvetica,Arial,sans-serif" ',
        1,
    )


def main() -> int:
    if not DATA.exists():
        print(f"no data at {DATA}, nothing to render", file=sys.stderr)
        return 0

    d = json.loads(DATA.read_text(encoding="utf-8"))
    ASSETS.mkdir(exist_ok=True)
    for theme in THEMES:
        (ASSETS / f"pulse-{theme}.svg").write_text(card(d, theme), encoding="utf-8")

    # Cache-buster: GitHub proxies images through camo and caches by URL, so a
    # changed file at an unchanged URL can serve stale for hours.
    v = re.sub(r"\D", "", d.get("generated_at", ""))[:14] or "0"
    base = "https://raw.githubusercontent.com/chaosen3/chaosen3/main/assets"
    block = f"""{START}
<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="{base}/pulse-dark.svg?v={v}">
    <img alt="Homelab pulse" src="{base}/pulse-light.svg?v={v}" width="840">
  </picture>
</p>
{END}"""

    text = README.read_text(encoding="utf-8")
    if START not in text or END not in text:
        print("README markers missing", file=sys.stderr)
        return 1
    new = re.sub(
        re.escape(START) + r".*?" + re.escape(END), lambda _: block, text, flags=re.S
    )
    if new != text:
        README.write_text(new, encoding="utf-8")
        print("README updated")
    else:
        print("README unchanged")
    return 0


if __name__ == "__main__":
    sys.exit(main())
