import sys
import tkinter as tk
from multiprocessing import Process, Value, Array, freeze_support
import time
import math
import random
import argparse

# Torus-Helferfunktion für Nachbarschaftszugriff
def torus_index(i, size):
    """Berechnet den torusförmigen Index."""
    return (i + size) % size

# Funktion für den einzelnen Glühwürmchen-Prozess
def firefly_process(x, y, phases, running, n, m, K, OMEGA):
    """Simuliert ein Glühwürmchen im Torus."""
    while running.value:
        neighbors_phase = 0
        neighbors_count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    nx = torus_index(x + dx, n)
                    ny = torus_index(y + dy, m)
                    neighbors_phase += phases[nx * m + ny]
                    neighbors_count += 1
        average_phase = neighbors_phase / neighbors_count
        idx = x * m + y
        phases[idx] = (phases[idx] + OMEGA + K * math.sin(average_phase - phases[idx])) % (2 * math.pi)
        time.sleep(0.08)

def main():
    # Parameter für die Simulation über Kommandozeilenargumente einlesen
    parser = argparse.ArgumentParser(description="Synchronisation der Glühwürmchen Simulation")
    parser.add_argument('n', type=int, help='Anzahl der Zeilen (Höhe des Gitters)')
    parser.add_argument('m', type=int, help='Anzahl der Spalten (Breite des Gitters)')
    parser.add_argument('--K', type=float, default=0.1, help='Kopplungsstärke (default: 0.1)')
    parser.add_argument('--OMEGA', type=float, default=0.75, help='Natürliche Frequenz (default: 0.75)')
    args = parser.parse_args()

    n = args.n
    m = args.m
    K = args.K
    OMEGA = args.OMEGA
    STEP_INTERVAL = 0.08  # Zeitintervall für die Updates

    # Ausgabe
    print(f"Anzahl der Spalten (m): {m}")
    print(f"Anzahl der Zeilen (n): {n}")
    print(f"Kopplungsstärke (k): {K}")
    print(f"Natürliche Frequenz (OMEGA): {OMEGA}")

    # Kontrollvariable zum Stoppen der Prozesse
    running = Value('b', True)  # Shared Boolean für alle Prozesse

    # Erstelle GUI
    root = tk.Tk()
    root.title("Synchronisation der Glühwürmchen")
    canvas = tk.Canvas(root, width=m * 50, height=n * 50)
    canvas.pack()

    # Initialisiere Glühwürmchen-Gitter
    rectangles = [[None for _ in range(m)] for _ in range(n)]

    # Gemeinsamer Speicher für Phasen der Glühwürmchen
    phases = Array('d', [random.uniform(0, 2 * math.pi) for _ in range(n * m)])


    # Prozesse für die Glühwürmchen erstellen
    processes = []
    for i in range(n):
        for j in range(m):
            x0, y0 = (j * 50, i * 50)
            x1, y1 = (x0 + 50, y0 + 50)
            rectangles[i][j] = canvas.create_rectangle(x0, y0, x1, y1, fill='black')
            p = Process(target=firefly_process, args=(i, j, phases, running, n, m, K, OMEGA))
            processes.append(p)
            p.start()

    # Funktion zur Aktualisierung der GUI
    def update_gui():
        if running.value:
            for i in range(n):
                for j in range(m):
                    idx = i * m + j
                    phase = phases[idx]
                    color = int((math.sin(phase) + 1) * 127.5)
                    canvas.itemconfig(rectangles[i][j], fill=f'#{color:02x}{color:02x}{color:02x}')
            root.after(int(STEP_INTERVAL * 1000), update_gui)

    # Funktion zum Beenden der Prozesse und Schließen des Programms
    def on_closing():
        running.value = False
        for p in processes:
            p.join()
        root.destroy()
        sys.exit()

    # Event-Handler für das Schließen des Fensters
    root.protocol("WM_DELETE_WINDOW", on_closing)

    # Starte die GUI-Aktualisierung
    update_gui()

    # Haupt-Loop für die GUI
    root.mainloop()

if __name__ == '__main__':
    freeze_support()  # Wichtig für Windows
    main()
