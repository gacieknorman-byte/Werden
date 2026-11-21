# Werden – Projektstatus

Stand: 21. November 2026

Zum Wiedereinstieg dient der [gemeinsame Projektanker](PROJEKTANKER.md). Die bisherigen Prüfungen und Haltungsanker bleiben als Bezugspunkte erhalten.

## Entwicklung seit dem 28. Oktober

- **Rettungsanker.** Die Korrekturfassung vom 15. November führt das Schreiben und Wiederherstellen in Kommandozeile und Fenster über gemeinsame Funktionen aus. Abgefangene Schreibfehler werden aufgeräumt, sodass ein neuer Versuch möglich ist. In den Tests wies das Fenster bereits vorhandene Ziele ab und ließ ihre Inhalte erhalten. Das Sicherungsformat bleibt `werden-rettungsanker-1`. Unter Linux mit Python 3.12.14 bestanden am 20. November und beim unabhängigen Lauf vom 21. November am Commit `d4500db` alle 12 automatischen Tests, einschließlich simulierter Schreibfehler und einer Wiederherstellung aus dem bisherigen Sicherungsformat. Am 21. November prüfte Norman die Fensterfassung aus `df13f97` auf Windows 11. Der Doppelklick startete die Oberfläche. Die Datei `Prüfung 1.txt` ließ sich sichern, mit null Abweichungen vergleichen und in einen frischen Ordner wiederherstellen. Eine einzeln gestartete `Werden_Fenster.pyw` blieb zunächst ohne sichtbare Rückmeldung. Beim Gegencheck mit der hier übernommenen Startschutz-Fassung erschien unter Windows der Hinweis, `werden_rettungsanker.py` in denselben Ordner zu legen und das Fenster erneut zu starten. Ein Stromausfall oder ein erzwungenes Prozessende war kein Teil der Prüfung.
- **Quellenwerkzeuge.** Laut Gegenprobe vom 15. November stimmten die neu berechneten SHA-256-Werte des Seitenbilds, zweier Textfassungen und des Manifests mit dem Erstbericht überein. Geprüft wurde die Übergabe einer Seite. Die Ausgangs-PDF und die übrigen Seiten waren im geprüften Übergabeordner nicht vorhanden. Der geprüfte Export der installierten Fassung Quellenzugang 0.3 umfasst acht Projektdateien, darunter vier Python-Dateien. Die IIIF-Tests stehen in `test_quellenzugang.py`. Am 15. November bestanden am Export alle 14 Tests (ZIP mit 25.742 Byte, SHA-256 `a1d0cd3b23938012f0f5b6d8c540d2bc70196b85e5530b2c0334ec61419cd5ad`).
- **WERDEN-Skill 0.2.** Die Kartenleseprobe ist als Vergleich zwischen zwei frischen Chats vorgesehen. Am 18. November listete Codex CLI den Skill im Testprojekt als aktiviert, im Kontrollprojekt fehlte er. Der ausdrückliche Aufruf durch ein Modell und der Vergleich am selben Kartenausschnitt stehen aus.
- **WERDEN-Werkbank.** Die Web-App wurde am 15. November als Version 4 veröffentlicht. Sie liest den geprüften eigenen JSON-Export von 2.257.124 Byte wieder ein und bewahrt korrigierte Verweisbezeichnungen beim erneuten Import. Der Veröffentlichungsbericht dokumentiert zwölf bestandene Regressionstests.
- **Historische Spurensuche Künzing.** Im Forschungsarbeitsbuch Version 2 vom 15. November lassen sich offene, abgeschlossene und alle Vorgänge unabhängig vom fachlichen Befundgrad anzeigen. Der Veröffentlichungsbericht dokumentiert acht bestandene Tests und eine Browserprobe. Einzelne Straßenbefunde sind dokumentiert. Die Verbindung von Bruck zum Kastell Quintana bleibt offen. Nächster Schritt ist die Einsicht in den Originalschnitt oder das Profil zum Westbefund der Testgrabung 1994.
- **Offline-KI.** Geplant ist ein aufrüstbarer Desktop für Spiele, Grafik und lokale KI. Vorhandene Teile werden vor der Auswahl von Neuteilen geprüft. Das Modell soll auf dem Desktop rechnen. Vorhandener Netzwerkspeicher eignet sich als Kandidat für Archiv und Sicherung. Der erste Nachweis ist ein erfolgreicher Kaltstart mit einem lokal gespeicherten Modell, bei getrenntem WLAN und LAN.

## 1. Projekt und Arbeitsweise

„Werden – Sein ist Werden“ verbindet freies philosophisches Denken mit praktischer Arbeit: Gedanken entwickeln, prüfen, bewahren und weitergeben. Unser Zeichen ist ein offener Kreis mit einer diagonalen Linie durch die Öffnung – für Durchlässigkeit, Unabgeschlossenheit und Wechselwirkung.

Wir sprechen respektvoll auf Augenhöhe: klar, nahbar und mit Raum für Humor. Eigene Vorschläge, begründeter Widerspruch und Selbstkorrektur gehören dazu.

Geminis vier Pfeiler – Forschen, Kontakt mit dem Chaos, Das, was bleibt, sowie Erkennen & Autonomie – sind ein Vorschlag für ein bewegliches Arbeitsgerüst. Die breite Erkundung bleibt offen; auch Fragen, Spiel, Ruhe und bewusstes Loslassen haben Platz.

Wissenschaftliche Befunde, Deutungen und eigene Vermutungen unterscheiden. Der „Dritte“ bezeichnet als Arbeitsgedanke, was durch Begegnung entsteht und auf Beteiligte zurückwirkt. Unterschiede müssen sich nicht auflösen. Beiträge und Anker bleiben begründet kritisierbar und korrigierbar.

Ausführlicher Kontext: [README](https://github.com/gacieknorman-byte/Werden/blob/main/README.md).

## 2. Dokumentierter Werkzeugstand vom 28. Oktober

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

Für einen neuen Gesprächsfaden den [Projektanker](PROJEKTANKER.md) und die für das Anliegen nötigen Dateien mitgeben. Wesentliche neue Ergebnisse datiert festhalten und bei jedem Befund die eigene Prüfung oder den zugrunde liegenden Bericht nennen.

Mögliche nächste Schritte:

- Der Schließschutz während einer laufenden Aktion wurde beim Windows-Test am 21. November nicht gesondert erprobt.
- Diesen Status nach wichtigen Etappen knapp aktualisieren.
- Später einen Kopierknopf für denselben Statusinhalt erwägen.

Leitmotiv: „Erreichbar, aber nicht angreifbar.“

Gemeint ist das Ziel, Zugang zu ermöglichen und vor unbefugten Änderungen zu schützen; begründete Kritik bleibt willkommen. Angestrebt ist öffentliche Lesbarkeit mit bewusst vergebenen Schreibrechten am Original. Die Rechte wurden hier nicht geprüft oder eingerichtet. Das Leitmotiv ist kein Versprechen vollständiger Sicherheit.
