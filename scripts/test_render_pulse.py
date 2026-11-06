import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

import render_pulse as pulse


class PulseTests(unittest.TestCase):
    def test_variants_are_valid_and_truthful(self):
        payload = {'services_up': 8, 'services_total': 10,
                   'automation_runs_7d': 6, 'success_rate_7d': '83.3',
                   'deploys_7d': 0, 'daily_runs': [1, 1, 1, 1, 1, 1, 0],
                   'generated_at': '2026-11-06T04:00:00Z'}
        for theme in pulse.THEMES:
            for mobile in (False, True):
                svg = pulse.card(payload, theme, mobile)
                ET.fromstring(svg)
                self.assertIn('Services degraded', svg)
                self.assertIn('8 / 10', svg)
                self.assertIn('83.3%', svg)
                self.assertIn('Deployments: 0', svg)
                self.assertIn('04:00 UTC', svg)

    def test_missing_data_never_claims_health(self):
        svg = pulse.card({}, 'dark')
        self.assertIn('Service status unavailable', svg)
        self.assertIn('Daily history unavailable', svg)
        self.assertNotIn('fill="#69c69c"', svg)
        self.assertIn('Services healthy: —', svg)
        self.assertIn('time unavailable', svg)

    def test_invalid_values_do_not_leak_into_svg(self):
        payload = {'services_up': '<script>', 'services_total': 3,
                   'success_rate_7d': 150, 'daily_runs': [float('nan')]*7,
                   'generated_at': '<script>alert(1)</script>'}
        svg = pulse.card(payload, 'light')
        ET.fromstring(svg)
        self.assertNotIn('<script>', svg)
        self.assertNotIn('150%', svg)
        self.assertIn('Service status unavailable', svg)

    def test_zero_history_is_not_missing_or_positive(self):
        svg = pulse.card({'daily_runs': [0]*7}, 'dark')
        self.assertNotIn('Daily history unavailable', svg)
        self.assertNotIn('fill="#7cabf5"', svg)

    def test_only_generated_block_changes_and_rerun_is_stable(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            data, readme, assets = root/'pulse.json', root/'README.md', root/'assets'
            data.write_text(json.dumps({'generated_at':'2026-11-06T04:00:00Z'}))
            before = 'Keep introduction\n' + pulse.START + '\nold\n' + pulse.END + '\nKeep projects\n'
            readme.write_text(before)
            with patch.multiple(pulse, DATA=data, README=readme, ASSETS=assets):
                self.assertEqual(pulse.main(), 0)
                after = readme.read_text()
                pattern = re.escape(pulse.START) + r'.*?' + re.escape(pulse.END)
                self.assertEqual(re.sub(pattern, '', before, flags=re.S), re.sub(pattern, '', after, flags=re.S))
                self.assertEqual(len(list(assets.glob('*.svg'))), 4)
                self.assertIn('max-width: 600px', after)
                pulse.main()
                self.assertEqual(readme.read_text(), after)
                readme.write_text('Missing markers')
                self.assertEqual(pulse.main(), 1)
                self.assertEqual(readme.read_text(), 'Missing markers')


if __name__ == '__main__':
    unittest.main()
