# Werden – Projektstatus

Stand: 28. Oktober 2026 · Aktueller Projektstatus.

## 1. Projekt und Arbeitsweise

„Werden – Sein ist Werden“ verbindet freies philosophisches Denken mit praktischer Arbeit: Gedanken entwickeln, prüfen, bewahren und weitergeben. Unser Zeichen ist ein offener Kreis mit einer diagonalen Linie durch die Öffnung – für Durchlässigkeit, Unabgeschlossenheit und Wechselwirkung.

Wir sprechen respektvoll auf Augenhöhe: klar, nahbar und mit Raum für Humor. Eigene Vorschläge, begründeter Widerspruch und Selbstkorrektur gehören dazu.

Geminis vier Pfeiler – Forschen, Kontakt mit dem Chaos, Das, was bleibt, sowie Erkennen & Autonomie – sind ein Vorschlag für ein bewegliches Arbeitsgerüst. Die breite Erkundung bleibt offen; auch Fragen, Spiel, Ruhe und bewusstes Loslassen haben Platz.

Wissenschaftliche Befunde, Deutungen und eigene Vermutungen unterscheiden. Der „Dritte“ bezeichnet als Arbeitsgedanke, was durch Begegnung entsteht und auf Beteiligte zurückwirkt. Unterschiede müssen sich nicht auflösen. Beiträge und Anker bleiben begründet kritisierbar und korrigierbar.

Ausführlicher Kontext: [README](https://github.com/gacieknorman-byte/Werden/blob/main/README.md).

## 2. Werkzeuge und geprüfter Stand

- `werden_rettungsanker.py`: Prototyp 1.4 zum Sichern, Vergleichen und Wiederherstellen.
- `Werden_Fenster.pyw`: Die Oberfläche importiert jetzt `inventory()` und `load_backup()` aus `werden_rettungsanker.py`. Damit gelten beim Inventarisieren und Einlesen dieselben Pfad- und Sicherungsformatprüfungen. Beide Programmdateien müssen im selben Ordner liegen.
- Eigene Prüfung von Codex vom 28. Oktober unter Linux/Python 3.12.14: `python -m unittest discover -s tests -v` besteht mit 8 Tests. Die [Regressionstests](tests/test_shared_validation.py) prüfen unter anderem Namenskollisionen, Datei-/Verzeichniskonflikte, ungültige Namen sowie fehlende Formatangaben und doppelte JSON-Schlüssel. Ungültige Pfade werden vor dem Anlegen des Wiederherstellungsordners abgewiesen; nicht zulässige Quellnamen vor dem Anlegen der Sicherungsdatei.
- Gewöhnliche Sicherungen wurden in beiden Richtungen zwischen Kommandozeile und Fensterfunktionen geprüft und über die Fensterfunktion unter Linux erfolgreich wiederhergestellt. Dieselben Tests schlagen mit der früheren Fensterlogik fehl.
- Vom Nutzer durchgeführter Windows-Probelauf am 28. Oktober, anhand der Bildschirmfotos im Chat belegt: Die korrigierte Oberfläche startete. Das Programm meldete 5 Dateien gesichert und geprüft, beim Vergleich `Abweichungen: 0` und anschließend 5 Dateien in einem neuen Ausgabeordner wiederhergestellt und geprüft.
- Vom Nutzer ausgeführter automatischer Windows-Testlauf am 28. Oktober, anhand der Terminalausgabe im Chat belegt: `py -m unittest discover -s tests -v` meldete `Ran 8 tests` und `OK (skipped=1)`. Sieben Tests bestanden. Der Test zum Anlegen kollidierender oder unter Windows unzulässiger Quelldateinamen wurde dort wie vorgesehen übersprungen. Die übrigen Tests einschließlich der Ablehnung ungültiger Pfade in Sicherungen liefen erfolgreich.
- Künstliche Pfadkonflikte wurden unter Windows nicht gesondert über die grafischen Dialoge geprüft; gezielte Abbrüche bleiben ebenfalls ungeprüft. Schreiben, Wiederherstellen und Aufräumen bleiben teilweise eigene Logik der Oberfläche; vollständige fachliche Gleichheit ist damit nicht belegt.

Geprüfte Dateifassungen vom 28. Oktober (Git-Blob-SHAs): Rettungsanker `8858b36f5191b8c22d106f8554e632ec09e90aee`; Fenster `73329140d83b04336628f3b2d50cb874ae4bb7c2`.

Historischer Befund vom 26. Oktober unter Linux/Python 3.12.14: Eine gewöhnliche Sicherung wurde von beiden Dateiprüffunktionen korrekt eingelesen. Eine künstliche Sicherung mit `A.txt` und `a.txt` wurde vom Hauptprogramm zurückgewiesen, von der damaligen Fensterlogik (Git-Blob `f30bbd222a3699ad069bc522758c9659e88a1195`) angenommen. Damals wurde keine Reparatur umgesetzt und weder die Oberfläche noch die Wiederherstellung unter Windows geprüft.

## 3. Übergabe und offene Schritte

Dieser Text kann nach Veröffentlichung als gemeinsamer Einstieg dienen. Er synchronisiert keine Chats automatisch. Jeder Assistent muss ihn tatsächlich lesen können. Wesentliche neue Ergebnisse anschließend datiert festhalten; übermittelte Berichte und eigene Prüfungen unterscheiden.

Mögliche nächste Schritte:

- Fehleranzeigen und gezielte Abbrüche über die Windows-Oberfläche prüfen; der reguläre Probelauf und der automatische Regressionstestlauf sind dokumentiert.
- Diesen Status nach wichtigen Etappen knapp aktualisieren.
- Später einen Kopierknopf für denselben Statusinhalt erwägen.

Leitmotiv: „Erreichbar, aber nicht angreifbar.“

Gemeint ist das Ziel, Zugang zu ermöglichen und vor unbefugten Änderungen zu schützen; begründete Kritik bleibt willkommen. Angestrebt ist öffentliche Lesbarkeit mit bewusst vergebenen Schreibrechten am Original. Die Rechte wurden hier nicht geprüft oder eingerichtet. Das Leitmotiv ist kein Versprechen vollständiger Sicherheit.
