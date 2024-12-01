import sys
import tkinter as tk
from multiprocessing import Process, Value, Array
import time
import math
import random

# Simulationseinstellungen
GRID_SIZE = 20  # Größe des Gitters (10x10 Torus)
K = 0.1  # Kopplungsstärke
STEP_INTERVAL = 0.08  # Zeitintervall für die Updates
OMEGA = 0.75  # Natürliche Frequenz

# Kontrollvariable zum Stoppen der Prozesse
running = Value('b', True)  # Shared Boolean für alle Prozesse

# Erstelle GUI
root = tk.Tk()
root.title("Synchronisation der Glühwürmchen")
canvas = tk.Canvas(root, width=GRID_SIZE*50, height=GRID_SIZE*50)
canvas.pack()

# Initialisiere Glühwürmchen-Gitter
rectangles = [[None for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

# Gemeinsamer Speicher für Phasen der Glühwürmchen
phases = Array('d', [random.uniform(0, 2 * math.pi) for _ in range(GRID_SIZE * GRID_SIZE)])


# Torus-Helferfunktionen für Nachbarschaftszugriff
def torus_index(i, n):
    return (i + n) % GRID_SIZE


# Funktion für den einzelnen Glühwürmchen-Prozess
def firefly_process(x, y, phases, running):
    while running.value:
        # Phase der Nachbarn sammeln und den Durchschnitt berechnen
        neighbors_phase = 0
        neighbors_count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx != 0 or dy != 0:
                    nx = torus_index(x + dx, GRID_SIZE)
                    ny = torus_index(y + dy, GRID_SIZE)
                    neighbors_phase += phases[nx * GRID_SIZE + ny]
                    neighbors_count += 1

        average_phase = neighbors_phase / neighbors_count

        # Kuramoto-Modell: Phase anpassen
        idx = x * GRID_SIZE + y
        phases[idx] += OMEGA + K * math.sin(average_phase - phases[idx])
        phases[idx] %= 2 * math.pi

        time.sleep(STEP_INTERVAL)


# Prozesse für die Glühwürmchen erstellen
processes = []
for i in range(GRID_SIZE):
    for j in range(GRID_SIZE):
        x0, y0 = (i * 50, j * 50)
        x1, y1 = (x0 + 50, y0 + 50)
        rectangles[i][j] = canvas.create_rectangle(x0, y0, x1, y1, fill='black')

        # Erstelle einen Prozess für jedes Glühwürmchen
        p = Process(target=firefly_process, args=(i, j, phases, running))
        processes.append(p)
        p.start()


# Funktion zur Aktualisierung der GUI
def update_gui():
    if running.value:
        for i in range(GRID_SIZE):
            for j in range(GRID_SIZE):
                idx = i * GRID_SIZE + j
                phase = phases[idx]
                color = int((math.sin(phase) + 1) * 127.5)
                canvas.itemconfig(rectangles[i][j], fill=f'#{color:02x}{color:02x}{color:02x}')
        root.after(int(STEP_INTERVAL * 1000), update_gui)


# Funktion zum Beenden der Prozesse und Schließen des Programms
def on_closing():
    running.value = False  # Prozesse stoppen
    for p in processes:
        p.join()  # Warten, bis alle Prozesse beendet sind
    root.destroy()
    sys.exit()


# Event-Handler für das Schließen des Fensters
root.protocol("WM_DELETE_WINDOW", on_closing)

# Starte die GUI-Aktualisierung
update_gui()

# Haupt-Loop für die GUI
root.mainloop()
