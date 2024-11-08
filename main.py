import tkinter as tk
from tkinter import scrolledtext
import serial
from serial.tools import list_ports
import threading
import time

class SerialApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Serial Data Logger")

        self.serial_port = None
        # Frame für die Textfelder und den Button
        frame = tk.Frame(root)
        frame.pack(pady=10)

        # Textfeld für die Live-Anzeige der aktuellen Zeile
        tk.Label(frame, text="Live-Daten").pack()
        self.live_display = tk.Text(frame, height=2, width=50, wrap=tk.WORD)
        self.live_display.pack(padx=10, pady=5)

        # ScrolledText für das Log der Snapshots
        tk.Label(frame, text="Snapshots").pack()
        self.snapshot_log = scrolledtext.ScrolledText(frame, width=50, height=15, wrap=tk.WORD)
        self.snapshot_log.pack(padx=10, pady=5)

        # Button für die Snapshot-Funktion
        self.button = tk.Button(frame, text="Snapshot speichern", command=self.save_snapshot)
        self.button.pack(pady=10)

        self.serial_port_name = 'COM9'
        self.setup_serial()

        # Fenster schließen und seriellen Port freigeben
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.buffer = b''
        self.root.after(100, self.read_serial_data)

    def save_snapshot(self):
        # Snapshot der aktuellen Zeile aus der Live-Anzeige ins Log kopieren
        current_line = self.live_display.get("1.0", tk.END).strip()  # Aktuelle Zeile holen
        if current_line:
            self.snapshot_log.insert(tk.END, current_line + "\n")
            self.snapshot_log.see(tk.END)  # Zum Ende des Logs scrollen

    def setup_serial(self):
        if self.serial_port is None:
            self.open_serial(self.serial_port_name)
        elif not self.serial_port.is_open:
            self.open_serial(self.serial_port_name)
        elif self.serial_port.port not in [e.name for e in list_ports.comports()]:
            self.serial_port = None
        self.root.after(500,self.setup_serial)


    def open_serial(self, port):
        # Serielle Schnittstelle initialisieren
        try:
            # Seriellen Port auf COM9 und Baudrate auf 115200 setzen
            self.serial_port = serial.Serial(port, baudrate=115200, timeout=1)
            print("Verbindung zur seriellen Schnittstelle hergestellt.")
        except serial.SerialException as e:
            print("Fehler beim Öffnen der seriellen Schnittstelle:", e)
            self.serial_port = None

    def close_serial(self):
        if self.serial_port:
            self.serial_port.close()  # Schließt die serielle Schnittstelle
            print("Verbindung zur seriellen Schnittstelle getrennt.")

    def read_serial_data(self):
        try:
            while self.serial_port and self.serial_port.in_waiting > 0:
                # Empfange und dekodiere die aktuelle Zeile
                #print("before")
                c = self.serial_port.read()
                #print("after")
                if c != b'\n':
                    self.buffer += c
                    continue
                data = self.buffer.decode('utf-8').strip()
                self.buffer = b''
                if data:
                    # Zeige die aktuelle empfangene Zeile in der Live-Anzeige an
                    self.live_display.delete("1.0", tk.END)  # Löscht den alten Inhalt
                    self.live_display.insert(tk.END, data)  # Fügt neuen Inhalt ein
        except Exception as e:
            print("Fehler beim Lesen der Daten:", e)
            self.buffer = b''
            #self.serial_port.close()
                    
        self.root.after(100, self.read_serial_data)


    def on_close(self):
        # Methode zum Schließen des Fensters und Beenden des Threads
        print("Schließe Anwendung...")
        # Warte, bis der Thread beendet ist
        self.close_serial()
        self.root.destroy()  # Beendet das Tkinter-Hauptfenster

# Tkinter-Root-Fenster erstellen
root = tk.Tk()
app = SerialApp(root)

# Hauptfenster starten
root.mainloop()

