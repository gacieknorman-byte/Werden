"""Regressionstests für die gemeinsamen Prüfungen, ohne ein Fenster zu öffnen.

Aufruf im Projektordner: python -m unittest discover -s tests -v
Python mit Tkinter wird auch für den Import der Fensterdatei benötigt.
"""
import base64
import hashlib
import importlib.machinery
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import werden_rettungsanker as core

loader = importlib.machinery.SourceFileLoader(
    'werden_fenster_tests', str(ROOT / 'Werden_Fenster.pyw'),
)
spec = importlib.util.spec_from_loader(loader.name, loader)
window = importlib.util.module_from_spec(spec)
loader.exec_module(window)


class SharedValidationTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory(prefix='werden-test-')
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.data = b'Werden\x00\xff\n'

    def backup(self, names):
        return {
            'format': 'werden-rettungsanker-1',
            'created_utc': '2026-10-28T00:00:00+00:00',
            'files': [
                {'path': name,
                 'sha256': hashlib.sha256(self.data).hexdigest(),
                 'data': base64.b64encode(self.data).decode('ascii')}
                for name in names
            ],
        }

    def write_backup(self, obj):
        path = self.root / 'backup.json'
        path.write_text(json.dumps(obj), encoding='utf-8')
        return path

    def project(self):
        source = self.root / 'project'
        (source / 'src').mkdir(parents=True)
        (source / 'src' / 'data.bin').write_bytes(self.data)
        (source / 'Grüße.txt').write_text('Sein ist Werden.\n', encoding='utf-8')
        return source

    def assert_same_files(self, source, restored):
        expected = {p.relative_to(source): p.read_bytes()
                    for p in source.rglob('*') if p.is_file()}
        actual = {p.relative_to(restored): p.read_bytes()
                  for p in restored.rglob('*') if p.is_file()}
        self.assertEqual(actual, expected)

    def assert_rejected_by_both(self, path):
        for module in (core, window):
            with self.subTest(module=module.__name__):
                with self.assertRaises(ValueError):
                    module.load_backup(path)

    def test_regular_backup_loads_in_both(self):
        names = ['src/data.bin', 'Grüße.txt']
        path = self.write_backup(self.backup(names))
        for module in (core, window):
            with self.subTest(module=module.__name__):
                self.assertEqual(module.load_backup(path),
                                 dict.fromkeys(names, self.data))

    def test_invalid_paths_rejected_before_restore_creates_destination(self):
        cases = [
            ['A.txt', 'a.txt'],
            ['Dir/a.txt', 'dir/b.txt'],
            ['a', 'a/b.txt'],
            ['a/b.txt', 'a'],
            ['a.txt', 'a.txt'],
            ['CON.txt'], ['a?.txt'], ['a.'], ['a '],
            ['a\x01.txt'], ['a\u200b.txt'],
            [''], ['/a.txt'], ['../a.txt'], ['./a.txt'],
            ['a//b.txt'], ['a\\b.txt'], ['a:b.txt'],
        ]
        for index, names in enumerate(cases):
            with self.subTest(paths=names):
                path = self.write_backup(self.backup(names))
                self.assert_rejected_by_both(path)
                destination = self.root / f'restored-{index}'
                with self.assertRaises(ValueError):
                    window.restore_project(path, destination)
                self.assertFalse(destination.exists())

    def test_missing_timestamp_is_rejected(self):
        obj = self.backup(['a.txt'])
        del obj['created_utc']
        self.assert_rejected_by_both(self.write_backup(obj))

    def test_additional_format_field_is_rejected(self):
        obj = self.backup(['a.txt'])
        obj['extra'] = True
        self.assert_rejected_by_both(self.write_backup(obj))

    def test_duplicate_json_key_is_rejected(self):
        path = self.write_backup(self.backup(['a.txt']))
        text = path.read_text(encoding='utf-8')
        path.write_text(text.replace('"format":',
                                    '"format": "ignored", "format":', 1),
                        encoding='utf-8')
        self.assert_rejected_by_both(path)

    @unittest.skipIf(os.name == 'nt',
                     'Diese Konfliktnamen lassen sich unter Windows nicht regulär anlegen.')
    def test_inventory_conflicts_cannot_be_saved_from_window(self):
        for index, names in enumerate([
            ['A.txt', 'a.txt'], ['Dir/a.txt', 'dir/b.txt'],
            ['CON.txt'], ['a?.txt'], ['a.'], ['a '],
        ]):
            with self.subTest(paths=names):
                source = self.root / f'project-{index}'
                for name in names:
                    path = source / name
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(self.data)
                actual = {p.relative_to(source).as_posix()
                          for p in source.rglob('*') if p.is_file()}
                if actual != set(names):
                    self.skipTest('Dateisystem erhält die Konfliktnamen nicht getrennt.')
                for module in (core, window):
                    with self.subTest(module=module.__name__):
                        with self.assertRaises(ValueError):
                            module.inventory(source)
                target = self.root / f'backup-{index}.json'
                with self.assertRaises(ValueError):
                    window.save_project(source, target)
                self.assertFalse(target.exists())

    def test_window_backup_is_readable_by_cli_and_restores(self):
        source = self.project()
        backup = self.root / 'window.json'
        window.save_project(source, backup)
        result = subprocess.run(
            [sys.executable, str(ROOT / 'werden_rettungsanker.py'),
             'pruefen', str(source), str(backup)],
            check=True, capture_output=True, text=True,
        )
        self.assertIn('Abweichungen: 0', result.stdout)
        self.assertIn('Abweichungen: 0', window.compare_project(source, backup))
        restored = self.root / 'restored'
        window.restore_project(backup, restored)
        self.assert_same_files(source, restored)

    def test_cli_backup_can_be_restored_from_window(self):
        source = self.project()
        backup = self.root / 'cli.json'
        subprocess.run(
            [sys.executable, str(ROOT / 'werden_rettungsanker.py'),
             'sichern', str(source), str(backup)],
            check=True, capture_output=True, text=True,
        )
        restored = self.root / 'restored'
        window.restore_project(backup, restored)
        self.assert_same_files(source, restored)


if __name__ == '__main__':
    unittest.main()
