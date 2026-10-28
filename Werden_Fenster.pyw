"""Werden – Dateien sichern, vergleichen und wiederherstellen.
Doppelklick unter Windows mit installiertem Python. Keine Zusatzpakete.
Kompatibel mit werden-rettungsanker-1. Sicherungen sind unverschlüsselt.
werden_rettungsanker.py muss im selben Ordner liegen.
"""
import argparse
import base64
import hashlib
import json
from pathlib import Path
from datetime import datetime, timezone

from werden_rettungsanker import inventory, load_backup


def digest(data):
    return hashlib.sha256(data).hexdigest()


import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading
import queue
import os


def save_project(source, target):
    root, target = Path(source).resolve(), Path(target).resolve()
    if target == root or root in target.parents:
        raise ValueError("Bitte die Sicherung außerhalb des gewählten Projektordners speichern.")
    entries = inventory(root)
    if not entries:
        raise ValueError("Der Ordner enthält keine sicherbaren Dateien. Es wurde keine Sicherung angelegt.")
    obj = {'format': 'werden-rettungsanker-1',
           'created_utc': datetime.now(timezone.utc).isoformat(),
           'files': [{'path': name, 'sha256': digest(data),
                      'data': base64.b64encode(data).decode('ascii')}
                     for name, data in entries.items()]}
    with target.open('x', encoding='utf-8') as out:
        json.dump(obj, out, ensure_ascii=False, indent=2)
    if load_backup(target) != entries:
        raise ValueError("Die neue Sicherung konnte nicht bestätigt werden.")
    return f"Gesichert und geprüft: {len(entries)} Dateien.\n\n{target}\n\nEine Kopie auf einem getrennten Datenträger aufbewahren."


def compare_project(source, backup):
    saved = load_backup(Path(backup))
    current = inventory(Path(source).resolve())
    changes = []
    for name in sorted(saved.keys() | current.keys()):
        state = ('NEU' if name not in saved else 'FEHLT' if name not in current
                 else 'VERÄNDERT' if saved[name] != current[name] else 'GLEICH')
        if state != 'GLEICH':
            changes.append(f"{state}: {name}")
    return f"Abweichungen: {len(changes)}\nÄnderungen können beabsichtigt sein.\n\n" + ('\n'.join(changes) or "Alle enthaltenen Dateien stimmen mit der Sicherung überein.")


def restore_project(backup, destination):
    saved = load_backup(Path(backup))
    root = Path(destination).resolve()
    root.mkdir(parents=True, exist_ok=False)
    for name, data in saved.items():
        target = root.joinpath(*name.split('/'))
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open('xb') as out:
            out.write(data)
        if digest(target.read_bytes()) != digest(data):
            raise ValueError("Wiederherstellung konnte nicht bestätigt werden: " + name)
    return f"Wiederhergestellt und geprüft: {len(saved)} Dateien.\n\n{root}\n\nDie Sicherungsdatei bleibt unverändert."


class WerdenWindow:
    def __init__(self, root):
        self.root = root
        self.events = queue.Queue()
        self.busy = False
        self.output_folder = None
        root.title("Werden – Rettungsanker")
        root.geometry("720x620")
        root.minsize(620, 520)
        root.protocol("WM_DELETE_WINDOW", self.close)
        style = ttk.Style(root)
        style.configure('TButton', font=('Segoe UI', 12), padding=10)
        style.configure('TLabel', font=('Segoe UI', 11))
        frame = ttk.Frame(root, padding=24)
        frame.pack(fill='both', expand=True)
        ttk.Label(frame, text="Werden – Rettungsanker", font=('Segoe UI', 22, 'bold')).pack(anchor='w')
        ttk.Label(frame, text="Sein ist Werden. Gedanken bewahren und weitergeben.").pack(anchor='w', pady=(4, 20))
        self.buttons = []
        for title, subtitle, callback in [
            ('Sichern', 'Projektordner wählen → neue Sicherungsdatei speichern', self.save),
            ('Prüfen', 'Projektordner mit einer vorhandenen Sicherung vergleichen', self.compare),
            ('Wiederherstellen', 'Sicherungsdatei wählen → geprüfte Kopien in einem neuen Ordner', self.restore)]:
            button = ttk.Button(frame, text=title, command=callback)
            button.pack(fill='x', pady=(4, 0))
            self.buttons.append(button)
            ttk.Label(frame, text=subtitle, wraplength=650).pack(anchor='w', pady=(2, 8))
        self.status = ttk.Label(frame, text="Bereit. Wähle eine der drei Aktionen.")
        self.status.pack(anchor='w', pady=(8, 4))
        self.result = tk.Text(frame, height=8, wrap='word', font=('Segoe UI', 11), state='disabled')
        self.result.pack(fill='both', expand=True)
        self.open_button = ttk.Button(frame, text="Wiederhergestellten Ordner öffnen", command=self.open_folder, state='disabled')
        self.open_button.pack(fill='x', pady=(8, 4))
        ttk.Label(frame, text="Für kleine Projekte. Sicherungen sind unverschlüsselt. Während der Sicherung Dateien nicht bearbeiten.", wraplength=650).pack(anchor='w')
        root.after(100, self.poll)

    def choose_backup(self):
        return filedialog.askopenfilename(parent=self.root, title="Sicherungsdatei auswählen", filetypes=[('Werden-Sicherung', '*.json'), ('Alle Dateien', '*.*')])

    def save(self):
        source = filedialog.askdirectory(parent=self.root, title="Welchen Projektordner möchtest du sichern?")
        if not source:
            return
        target = filedialog.asksaveasfilename(parent=self.root, title="Neue Sicherung speichern – außerhalb des Projektordners", initialfile='Werden_Sicherung_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S') + '.json', defaultextension='.json', filetypes=[('Werden-Sicherung', '*.json')])
        if target:
            self.run(lambda: save_project(source, target))

    def compare(self):
        source = filedialog.askdirectory(parent=self.root, title="Welchen Projektordner möchtest du prüfen?")
        if not source:
            return
        backup = self.choose_backup()
        if backup:
            self.run(lambda: compare_project(source, backup))

    def restore(self):
        backup = self.choose_backup()
        if not backup:
            return
        parent = filedialog.askdirectory(parent=self.root, title="Wo soll der neue Wiederherstellungsordner entstehen?")
        if not parent:
            return
        destination = Path(parent) / ('Werden_Gerettet_' + datetime.now().strftime('%Y-%m-%d_%H-%M-%S_%f'))
        if messagebox.askokcancel("Wiederherstellen", f"Geprüfte Kopien werden hier abgelegt:\n\n{destination}\n\nDie Sicherungsdatei bleibt unverändert.", parent=self.root):
            self.run(lambda: restore_project(backup, destination), destination)

    def run(self, action, folder=None):
        self.busy = True
        for button in self.buttons:
            button.configure(state='disabled')
        self.open_button.configure(state='disabled')
        self.status.configure(text="Bitte warten …")
        def work():
            try:
                self.events.put((True, action(), folder))
            except Exception as exc:
                detail = str(exc)
                if isinstance(exc, FileExistsError):
                    detail = "Dieser Name ist bereits vergeben. Bitte einen neuen Namen wählen."
                self.events.put((False, "Abbruch: " + detail + "\n\nBei einer unterbrochenen Wiederherstellung kann ein unvollständiger Ausgabeordner zurückbleiben. Die Sicherungsdatei bleibt erhalten.", None))
        threading.Thread(target=work, daemon=True).start()

    def poll(self):
        try:
            ok, result, folder = self.events.get_nowait()
        except queue.Empty:
            pass
        else:
            self.busy = False
            self.output_folder = folder if ok else None
            self.status.configure(text="Fertig." if ok else "Die Aktion wurde abgebrochen.")
            self.result.configure(state='normal')
            self.result.delete('1.0', 'end')
            self.result.insert('1.0', result)
            self.result.configure(state='disabled')
            for button in self.buttons:
                button.configure(state='normal')
            if self.output_folder:
                self.open_button.configure(state='normal')
        self.root.after(100, self.poll)

    def open_folder(self):
        if self.output_folder:
            try:
                os.startfile(str(self.output_folder))
            except OSError as exc:
                messagebox.showerror("Ordner öffnen", str(exc), parent=self.root)

    def close(self):
        if self.busy:
            messagebox.showinfo("Bitte warten", "Die Aktion läuft noch. Schließe das Fenster nach Abschluss.", parent=self.root)
        else:
            self.root.destroy()


if __name__ == '__main__':
    root = tk.Tk()
    WerdenWindow(root)
    root.mainloop()
