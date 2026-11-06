#!/usr/bin/env python3
"""Render the existing pulse payload as responsive, themed SVGs. Stdlib only."""
from __future__ import annotations

import json
import math
from pathlib import Path
import re
import sys
from datetime import datetime, timezone
from html import escape

ROOT = Path(__file__).resolve().parent.parent
DATA, README, ASSETS = ROOT / 'data/pulse.json', ROOT / 'README.md', ROOT / 'assets'
START, END = '<!-- pulse:start -->', '<!-- pulse:end -->'
THEMES = {
    'dark': dict(bg='#0d1117', line='#303b49', text='#ecf2f8', muted='#99a8b9', accent='#7cabf5', good='#69c69c', warning='#e3b76a'),
    'light': dict(bg='#ffffff', line='#d5deea', text='#152438', muted='#52647b', accent='#285fba', good='#23734e', warning='#8c5b0b'),
}


def number(value):
    if isinstance(value, bool):
        return None
    try:
        n = float(value)
    except (TypeError, ValueError):
        return None
    return n if math.isfinite(n) and n >= 0 else None


def fmt(value):
    return f'{value:g}' if value is not None else '—'


def text(x, y, value, colour, size=13, weight=400, anchor='start'):
    return f'<text x="{x}" y="{y}" fill="{colour}" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}">{escape(str(value))}</text>'


def card(d, theme, mobile=False):
    t = THEMES[theme]
    w, h = (420, 364) if mobile else (840, 282)
    up, total = number(d.get('services_up')), number(d.get('services_total'))
    known = up is not None and total is not None and total > 0 and up <= total
    status = 'Services healthy' if known and up == total else ('Services degraded' if known else 'Service status unavailable')
    state_colour = t['good'] if known and up == total else (t['warning'] if known else t['muted'])
    success = number(d.get('success_rate_7d'))
    if success is not None and success > 100:
        success = None
    metrics = [
        ('Services healthy', f'{fmt(up)} / {fmt(total)}' if known else '—', 'at snapshot', state_colour),
        ('Automation runs', fmt(number(d.get('automation_runs_7d'))), 'last 7 days', t['text']),
        ('Execution success', fmt(success) + '%' if success is not None else '—', 'last 7 days', t['text']),
        ('Deployments', fmt(number(d.get('deploys_7d'))), 'last 7 days', t['text']),
    ]
    desc = '; '.join(f'{label}: {value} ({sub})' for label, value, sub, _ in metrics)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-labelledby="title desc" font-family="Segoe UI,Helvetica,Arial,sans-serif">',
             '<title id="title">Homelab pulse</title>', f'<desc id="desc">{escape(desc)}</desc>',
             f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="12" fill="{t["bg"]}" stroke="{t["line"]}"/>',
             text(24, 32, 'Homelab pulse', t['text'], 18, 600)]
    if mobile:
        parts.append(text(24, 52, status, state_colour, 12))
    else:
        parts.append(text(w-24, 32, status, state_colour, 12, anchor='end'))
    cols = 2 if mobile else 4
    cell = (w-48) / cols
    for i, (label, value, sub, colour) in enumerate(metrics):
        x = 24 + (i % cols) * cell
        y = (78 if mobile else 77) + (i // cols) * 88
        size = 32 if mobile else 36
        if len(value) > 10:
            size = 23
        parts.extend([text(x, y, label, t['muted'], 12), text(x, y+35, value, colour, size, 600), text(x, y+55, sub, t['muted'], 11)])
    rule_y, chart_title, baseline, footer = (235, 256, 311, 344) if mobile else (158, 182, 231, 263)
    parts.append(f'<path d="M24 {rule_y}H{w-24}" stroke="{t["line"]}"/>')
    parts.append(text(24, chart_title, 'Automation runs / day', t['muted'], 12))
    series = d.get('daily_runs')
    valid = isinstance(series, list) and len(series) == 7 and all(number(v) is not None for v in series)
    if valid:
        values = [number(v) for v in series]
        step = (w-48) / 7
        peak = max(values) or 1
        for i, value in enumerate(values):
            x, width = 24 + i * step, step-8
            height = value / peak * 24
            parts.append(f'<rect x="{x:.1f}" y="{baseline}" width="{width:.1f}" height="1" fill="{t["line"]}"/>')
            if value > 0:
                parts.append(f'<rect x="{x:.1f}" y="{baseline-height:.1f}" width="{width:.1f}" height="{height:.1f}" rx="2" fill="{t["accent"]}"/>')
            parts.append(text(round(x+width/2, 1), baseline-height-6, fmt(value), t['muted'], 11, anchor='middle'))
    else:
        parts.append(text(24, baseline-8, 'Daily history unavailable', t['muted'], 12))
    try:
        timestamp = datetime.fromisoformat(str(d.get('generated_at', '')).replace('Z', '+00:00'))
        if timestamp.tzinfo is None:
            raise ValueError('Timestamp must carry its timezone')
        stamp = timestamp.astimezone(timezone.utc).strftime('%d %b %Y · %H:%M UTC')
    except ValueError:
        stamp = 'time unavailable'
    parts.extend([text(24, footer, f'Snapshot · {stamp}', t['muted'], 11), '</svg>'])
    return '\n'.join(parts) + '\n'


def main():
    if not DATA.exists():
        print('No pulse data; nothing to render', file=sys.stderr)
        return 0
    content = README.read_text(encoding='utf-8')
    if content.count(START) != 1 or content.count(END) != 1 or content.index(START) > content.index(END):
        print('README needs one ordered pair of pulse markers', file=sys.stderr)
        return 1
    d = json.loads(DATA.read_text(encoding='utf-8'))
    if not isinstance(d, dict):
        raise ValueError('Pulse payload must be an object')
    ASSETS.mkdir(exist_ok=True)
    for theme in THEMES:
        for mobile in (False, True):
            suffix = '-mobile' if mobile else ''
            (ASSETS / f'pulse-{theme}{suffix}.svg').write_text(card(d, theme, mobile), encoding='utf-8')
    version = '2-' + (re.sub(r'\D', '', str(d.get('generated_at', '')))[:14] or '0')
    base = 'https://raw.githubusercontent.com/chaosen3/chaosen3/main/assets'
    block = f'''{START}
<picture>
  <source media="(prefers-color-scheme: dark) and (max-width: 600px)" srcset="{base}/pulse-dark-mobile.svg?v={version}">
  <source media="(prefers-color-scheme: dark)" srcset="{base}/pulse-dark.svg?v={version}">
  <source media="(max-width: 600px)" srcset="{base}/pulse-light-mobile.svg?v={version}">
  <img alt="Homelab pulse: service health, automation runs, execution success and deployments; collection time shown in the panel" src="{base}/pulse-light.svg?v={version}" width="840">
</picture>
{END}'''
    new = re.sub(re.escape(START)+r'.*?'+re.escape(END), lambda _: block, content, flags=re.S)
    if new != content:
        README.write_text(new, encoding='utf-8')
    print('Rendered four pulse variants')
    return 0


if __name__ == '__main__':
    sys.exit(main())

