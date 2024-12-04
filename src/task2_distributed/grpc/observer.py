import grpc
import fireflys_pb2
import fireflys_pb2_grpc
import tkinter as tk
import time
import math
from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor

class Observer:
    def __init__(self, n, m, firefly_host="localhost"):
        """
        Initialisiert den Observer.
        :param n: Anzahl der Zeilen im Gitter
        :param m: Anzahl der Spalten im Gitter
        :param firefly_host: Basisadresse der Fireflies (z. B. 'localhost' oder IP-Adresse)
        """
        self.n = n
        self.m = m
        self.firefly_host = firefly_host  # Basisadresse der Fireflies
        self.phases = [0] * (n * m)  # Phasen aller Glühwürmchen
        self.executor = ThreadPoolExecutor(max_workers=10)  # Thread-Pool für parallele Abfragen
        self.latencies = []  # Liste zur Speicherung der Latenzen
        self.latency_lock = Lock()  # Lock für thread-sicheren Zugriff auf die Latenzliste

    def fetch_phases(self):
        """Fragt regelmäßig die Phasen aller Glühwürmchen ab."""
        def query_firefly(i):
            """Hilfsfunktion, um die Phase eines einzelnen Glühwürmchens abzufragen."""
            address = f"{self.firefly_host}:{5001 + i}"  # Dynamische Adresse basierend auf ID
            try:
                start_time = time.time()  # Startzeit der Anfrage
                with grpc.insecure_channel(address) as channel:
                    stub = fireflys_pb2_grpc.FireflyStub(channel)
                    response = stub.GetPhase(fireflys_pb2.PhaseRequest(id=i))
                    end_time = time.time()  # Endzeit der Antwort
                    latency = (end_time - start_time) * 1000  # Latenz in Millisekunden

                    # Speichere die Latenz thread-sicher
                    with self.latency_lock:
                        self.latencies.append(latency)

                    self.phases[i] = response.phase  # Phase speichern
            except grpc.RpcError:
                pass  # Ignoriere Verbindungsfehler

        while True:
            # Parallele Abfragen aller Fireflies
            self.executor.map(query_firefly, range(self.n * self.m))
            time.sleep(0.08)  # Intervall zwischen Anfragen

    def calculate_and_print_latency_stats(self):
        """Berechnet und gibt die Latenzstatistiken aus."""
        while True:
            time.sleep(5)  # Statistiken alle 5 Sekunden ausgeben
            with self.latency_lock:
                if self.latencies:
                    max_latency = max(self.latencies)
                    min_latency = min(self.latencies)
                    avg_latency = sum(self.latencies) / len(self.latencies)
                    print(f"Latency Stats: Max: {max_latency:.2f} ms, Min: {min_latency:.2f} ms, Avg: {avg_latency:.2f} ms")
                    self.latencies.clear()  # Zurücksetzen der Liste nach Ausgabe
                else:
                    print("Latency Stats: No data collected in the last interval.")

    def visualize(self):
        """Visualisiert die Zustände der Glühwürmchen."""
        root = tk.Tk()
        root.title("Firefly Observer")

        canvas = tk.Canvas(root, width=self.m * 50, height=self.n * 50)
        canvas.pack()

        # Rechtecke für die Visualisierung erstellen
        rectangles = [[None for _ in range(self.m)] for _ in range(self.n)]
        for i in range(self.n):
            for j in range(self.m):
                x0, y0 = (j * 50, i * 50)
                x1, y1 = (x0 + 50, y0 + 50)
                rectangles[i][j] = canvas.create_rectangle(x0, y0, x1, y1, fill='black')

        def update_gui():
            """Aktualisiert die GUI basierend auf den Phasen."""
            for i in range(self.n):
                for j in range(self.m):
                    idx = i * self.m + j
                    phase = self.phases[idx]
                    color = int((math.sin(phase) + 1) * 127.5)  # Phase -> Farbe
                    canvas.itemconfig(rectangles[i][j], fill=f'#{color:02x}{color:02x}{color:02x}')
            root.after(500, update_gui)  # Aktualisierungsintervall auf 500 ms gesetzt

        update_gui()
        root.mainloop()

    def start(self):
        """Startet die Phasenabfrage und die Visualisierung."""
        Thread(target=self.fetch_phases, daemon=True).start()
        Thread(target=self.calculate_and_print_latency_stats, daemon=True).start()
        self.visualize()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Firefly Observer")
    parser.add_argument("--n", type=int, required=True, help="Anzahl der Zeilen")
    parser.add_argument("--m", type=int, required=True, help="Anzahl der Spalten")
    parser.add_argument("--firefly-host", type=str, default="localhost", help="Host-Adresse der Fireflies (Standard: localhost)")
    args = parser.parse_args()

    # Starte den Observer
    observer = Observer(args.n, args.m, firefly_host=args.firefly_host)
    observer.start()
