#!/usr/bin/env python3
"""Werden – Rettungsanker, Prototyp 1 (Python 3, keine Zusatzpakete).

Zweck: Einen gesicherten Dateistand bewahren, spätere Abweichungen erkennen
und nach Verlust eine überprüfte Kopie wiederherstellen. Originale bleiben
unverändert. Sicherungen enthalten die vollständigen Daten, unverschlüsselt.

Aufruf:
  python werden_rettungsanker.py sichern projekt sicherung.json
  python werden_rettungsanker.py pruefen projekt sicherung.json
  python werden_rettungsanker.py retten sicherung.json neuer_ordner

Sicherung außerhalb des Projektordners speichern und zusätzlich auf einem
anderen Datenträger aufbewahren. Jede Sicherung braucht einen neuen Namen.
Eine Abweichung kann auch eine gewollte Bearbeitung sein; sie ist kein
Beweis für Verfall. Fehlende Bytes ohne erhaltene Kopie werden nicht erfunden.
Identische Dateien sind keine unabhängigen Quellen. Dieses Werkzeug erkennt
Byte-Gleichheit, aber keine inhaltliche Wahrheit, Quellenabhängigkeit oder
Qualitätsverluste durch wiederholtes KI-Training. Dafür braucht es zusätzlich
Quellenherkunft, unabhängige Vergleichsdaten und menschliche Prüfung.

Grenzen: Keine Rettung defekter Datenträger, kein laufender Dienst, keine
konsistenten Sicherungen während gleichzeitiger Bearbeitung, keine Metadaten-
oder Rechtewiederherstellung. Für kleine Projekte: Dateien werden in den
Arbeitsspeicher geladen. Symlinks werden ausgelassen. JSON-Sicherung und ihre
Prüfsummen sind kein Schutz vor absichtlicher Manipulation. Vorlage für einen
konkreten Weg zum Weitergehen, kein universelles Heilungsversprechen.
"""
import argparse
import base64
import hashlib
import json
import re
from pathlib import Path
from datetime import datetime, timezone


def digest(data):
    return hashlib.sha256(data).hexdigest()


def inventory(root):
    if not root.is_dir():
        raise ValueError('Projektordner fehlt.')
    result = {}
    for path in sorted(root.rglob('*')):
        if path.is_symlink() or any(p.is_symlink() for p in path.parents):
            continue
        if path.is_file():
            result[path.relative_to(root).as_posix()] = path.read_bytes()
    return result


def load_backup(path):
    obj = json.loads(path.read_text(encoding='utf-8'))
    if obj.get('format') != 'werden-rettungsanker-1':
        raise ValueError('Unbekanntes Sicherungsformat.')
    result = {}
    for row in obj['files']:
        name = row['path']
        parts = name.split('/')
        if (not name or '\\' in name or ':' in name or
                any(p in ('', '.', '..') for p in parts) or name in result):
            raise ValueError('Unsicherer oder doppelter Dateipfad.')
        data = base64.b64decode(row['data'], validate=True)
        if not re.fullmatch(r'[0-9a-f]{64}', row['sha256']) or digest(data) != row['sha256']:
            raise ValueError('Beschädigte Sicherung: ' + name)
        result[name] = data
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('aktion', choices=['sichern', 'pruefen', 'retten'])
    parser.add_argument('quelle', type=Path)
    parser.add_argument('ziel', type=Path)
    args = parser.parse_args()
    if args.aktion == 'sichern':
        root, target = args.quelle.resolve(), args.ziel.resolve()
        if target == root or root in target.parents:
            raise ValueError('Sicherung muss außerhalb des Projektordners liegen.')
        entries = inventory(root)
        obj = {'format': 'werden-rettungsanker-1',
               'created_utc': datetime.now(timezone.utc).isoformat(),
               'files': [{'path': name, 'sha256': digest(data),
                          'data': base64.b64encode(data).decode('ascii')}
                         for name, data in entries.items()]}
        with target.open('x', encoding='utf-8') as out:
            json.dump(obj, out, ensure_ascii=False, indent=2)
        print('Gesichert:', len(entries), 'Dateien. Kopie getrennt aufbewahren.')
    elif args.aktion == 'pruefen':
        saved = load_backup(args.ziel)
        current = inventory(args.quelle.resolve())
        problems = 0
        for name in sorted(saved.keys() | current.keys()):
            state = ('NEU' if name not in saved else 'FEHLT' if name not in current
                     else 'VERÄNDERT' if saved[name] != current[name] else 'GLEICH')
            if state != 'GLEICH':
                problems += 1
                print(state + ': ' + name)
        groups = {}
        for name, data in current.items():
            groups.setdefault(digest(data), []).append(name)
        for names in groups.values():
            if len(names) > 1:
                print('IDENTISCHE BYTES (keine unabhängigen Belege):', ', '.join(names))
        print('Abweichungen:', problems, '(Änderungen können beabsichtigt sein.)')
    else:
        saved = load_backup(args.quelle)
        root = args.ziel.resolve()
        root.mkdir(parents=True, exist_ok=False)
        for name, data in saved.items():
            target = root.joinpath(*name.split('/'))
            target.parent.mkdir(parents=True, exist_ok=True)
            with target.open('xb') as out:
                out.write(data)
            if digest(target.read_bytes()) != digest(data):
                raise ValueError('Wiederherstellung konnte nicht bestätigt werden: ' + name)
        print('Überprüfte Kopien wiederhergestellt:', len(saved), 'Originale unverändert.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise SystemExit('Abbruch: ' + str(exc))
