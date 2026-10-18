#!/usr/bin/env python3
"""Werden – Rettungsanker, Prototyp 1.4 (Python 3, keine Zusatzpakete).

Bewahrt Dateistände, erkennt Abweichungen und stellt geprüfte Kopien wieder her.
Originale bleiben unverändert. Sicherungen enthalten vollständige Daten,
unverschlüsselt. Sie müssen außerhalb des Projektordners gespeichert werden.
Jede Sicherung und jeder Wiederherstellungsordner braucht einen neuen Namen.

Aufruf:
  python werden_rettungsanker.py sichern projekt sicherung.json
  python werden_rettungsanker.py pruefen projekt sicherung.json
  python werden_rettungsanker.py retten sicherung.json neuer_ordner

Eine Kopie auf einem getrennten Datenträger aufbewahren. Änderungen können
beabsichtigt sein; eine Abweichung ist kein Beweis für Verfall. Identische
Dateien sind keine unabhängigen Quellen. Prüfsummen prüfen Bytes, keine
inhaltliche Wahrheit und keine Qualität von KI-Trainingsdaten.

Grenzen: Für kleine Projekte; Dateien werden in den Arbeitsspeicher geladen.
Keine Rettung defekter Datenträger, kein laufender Dienst, keine Metadaten-
oder Rechtewiederherstellung. Leere Ordner und Symlinks werden ausgelassen.
Während der Arbeit dürfen Quelldateien, Zielpfade und Verzeichnisse nicht
gleichzeitig verändert werden. Schutz gegen absichtliche Manipulation oder
Pfadaustausch während der Ausführung ist nicht garantiert. Bei Stromausfall
oder hartem Prozessabbruch können unvollständige Ziele zurückbleiben.
"""
import argparse
import base64
import hashlib
import json
import os
import re
import shutil
from datetime import datetime, timezone
from pathlib import Path

RESERVED_WIN = re.compile(
    r'^(CON|PRN|AUX|NUL|CONIN\$|CONOUT\$|(COM|LPT)[0-9\xb9\xb2\xb3])$',
    re.IGNORECASE,
)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def ensure_no_symlink(path):
    full = path if path.is_absolute() else Path.cwd() / path
    if full.is_symlink() or any(p.is_symlink() for p in full.parents):
        raise ValueError('Symlinks im Pfad werden nicht unterstützt: ' + str(path))


def valid_relpath(name):
    if not name or '\\' in name or ':' in name:
        return False
    for part in name.split('/'):
        if not part or part in ('.', '..') or part[-1] in (' ', '.'):
            return False
        if any(ord(c) < 32 or 127 <= ord(c) <= 159 or
               not c.isprintable() or c in '<>:"|?*' for c in part):
            return False
        if RESERVED_WIN.fullmatch(part.split('.')[0]):
            return False
    return True


def register_path(nodes, name):
    if not valid_relpath(name):
        raise ValueError('Unsicherer oder ungültiger Dateipfad: ' + name)
    parts = name.split('/')
    folded = tuple(p.casefold() for p in parts)
    for i in range(1, len(parts)):
        prefix = folded[:i]
        prev = nodes.setdefault(prefix, ('dir', parts[i - 1]))
        if prev != ('dir', parts[i - 1]):
            raise ValueError('Pfadkonflikt im Verzeichnisbaum: ' + name)
    if folded in nodes:
        raise ValueError('Doppelter oder kollidierender Dateipfad: ' + name)
    nodes[folded] = ('file', parts[-1])


def unique_dict(pairs):
    obj = {}
    for key, val in pairs:
        if key in obj:
            raise ValueError('Doppelter JSON-Schlüssel: ' + str(key))
        obj[key] = val
    return obj


def inventory(source):
    ensure_no_symlink(source)
    if not source.is_dir():
        raise ValueError('Projektordner fehlt.')
    root = source.resolve()
    stack, files = [root], []
    while stack:
        cur = stack.pop()
        for entry in sorted(cur.iterdir(), reverse=True):
            entry.lstat()
            if entry.is_symlink():
                continue
            if entry.is_dir():
                stack.append(entry)
            elif entry.is_file():
                files.append(entry)
            else:
                raise ValueError('Nicht unterstützter Dateityp: ' + str(entry))
    result, nodes = {}, {}
    for path in sorted(files):
        name = path.relative_to(root).as_posix()
        register_path(nodes, name)
        result[name] = path.read_bytes()
    return result


def load_backup(path):
    ensure_no_symlink(path)
    if not path.is_file():
        raise ValueError('Sicherungsdatei fehlt.')
    obj = json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_dict)
    if (not isinstance(obj, dict) or
            obj.get('format') != 'werden-rettungsanker-1' or
            set(obj) != {'format', 'created_utc', 'files'} or
            not isinstance(obj.get('created_utc'), str)):
        raise ValueError('Unbekanntes oder beschädigtes Sicherungsformat.')
    files = obj['files']
    if not isinstance(files, list):
        raise ValueError('Beschädigte Dateiliste in der Sicherung.')
    result, nodes = {}, {}
    for row in files:
        if not isinstance(row, dict) or set(row) != {'path', 'sha256', 'data'}:
            raise ValueError('Ungültiger Dateieintrag in der Sicherung.')
        name, sha, b64 = row['path'], row['sha256'], row['data']
        if not all(isinstance(x, str) for x in (name, sha, b64)):
            raise ValueError('Unvollständiger Dateieintrag in der Sicherung.')
        register_path(nodes, name)
        data = base64.b64decode(b64, validate=True)
        if not re.fullmatch(r'[0-9a-f]{64}', sha) or digest(data) != sha:
            raise ValueError('Beschädigte Sicherung: ' + name)
        result[name] = data
    return result


def write_checked(path, data):
    out = path.open('xb')
    try:
        with out:
            out.write(data)
            out.flush()
            os.fsync(out.fileno())
        if path.read_bytes() != data:
            raise ValueError('Geschriebene Datei stimmt nicht überein: ' + str(path))
    except BaseException as exc:
        try:
            path.unlink()
        except OSError as cleanup_exc:
            raise OSError(
                f'{exc} (Aufräumen von {path} fehlgeschlagen: {cleanup_exc})'
            ) from exc
        raise


def main():
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('aktion', choices=['sichern', 'pruefen', 'retten'])
    parser.add_argument('quelle', type=Path)
    parser.add_argument('ziel', type=Path)
    args = parser.parse_args()
    if args.aktion == 'sichern':
        ensure_no_symlink(args.quelle)
        ensure_no_symlink(args.ziel)
        if args.ziel.exists():
            raise ValueError('Zieldatei existiert bereits.')
        root, target = args.quelle.resolve(), args.ziel.resolve()
        if target == root or root in target.parents:
            raise ValueError('Sicherung muss außerhalb des Projektordners liegen.')
        if not target.parent.is_dir():
            raise ValueError('Zielordner für die Sicherung fehlt.')
        entries = inventory(args.quelle)
        obj = {
            'format': 'werden-rettungsanker-1',
            'created_utc': datetime.now(timezone.utc).isoformat(),
            'files': [
                {'path': name, 'sha256': digest(data),
                 'data': base64.b64encode(data).decode('ascii')}
                for name, data in entries.items()
            ],
        }
        payload = (json.dumps(obj, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
        write_checked(target, payload)
        print('Gesichert und geprüft:', len(entries), 'Dateien. Kopie getrennt aufbewahren.')
    elif args.aktion == 'pruefen':
        saved, current = load_backup(args.ziel), inventory(args.quelle)
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
        ensure_no_symlink(args.ziel)
        if args.ziel.exists():
            raise ValueError('Zielordner existiert bereits.')
        saved = load_backup(args.quelle)
        root = args.ziel.resolve()
        if not root.parent.is_dir():
            raise ValueError('Übergeordneter Ordner für das Rettungsziel fehlt.')
        root.mkdir(parents=False, exist_ok=False)
        try:
            for name, data in saved.items():
                target = root.joinpath(*name.split('/'))
                target.parent.mkdir(parents=True, exist_ok=True)
                write_checked(target, data)
        except BaseException as exc:
            if root.exists():
                try:
                    shutil.rmtree(root)
                except OSError as cleanup_exc:
                    raise OSError(
                        f'{exc} (Aufräumen von {root} fehlgeschlagen: {cleanup_exc})'
                    ) from exc
            raise
        print('Überprüfte Kopien wiederhergestellt:', len(saved), 'Originale unverändert.')


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        raise SystemExit('Abbruch: Vorgang durch Benutzer unterbrochen.')
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise SystemExit('Abbruch: ' + str(exc))
