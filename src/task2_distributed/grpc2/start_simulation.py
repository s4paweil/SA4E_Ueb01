import subprocess
import time

# Parameter der Simulation
n, m = 10, 20  # Anzahl der Zeilen und Spalten
observer_port = 5000
simulation_duration = 300  # Dauer der Simulation in Sekunden

# Starte den Observer
observer_process = subprocess.Popen(["python", "observer.py", "--n", str(n), "--m", str(m), "--port", str(observer_port)])

# Starte Firefly-Prozesse
firefly_processes = []
for i in range(n):
    for j in range(m):
        id = i * m + j
        port = 5001 + id
        neighbors = [
            f"localhost:{5001 + ((i + dx) % n) * m + ((j + dy) % m)}"
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]
        ]
        firefly_processes.append(subprocess.Popen([
            "python", "firefly.py",
            "--id", str(id),
            "--neighbors", *neighbors,
            "--observer", f"localhost:{observer_port}",
            "--port", str(port)
        ]))

# Warte für die angegebene Dauer und beende dann die Firefly-Prozesse
time.sleep(simulation_duration)
for process in firefly_processes:
    process.terminate()
    process.wait()

print("Firefly-Prozesse beendet. Der Observer läuft weiter.")
