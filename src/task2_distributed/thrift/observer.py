from gen_py.fireflys import FireflyService
from thrift.transport import TSocket, TTransport
from thrift.protocol import TBinaryProtocol
import tkinter as tk
import time
import math
from threading import Thread, Lock
from concurrent.futures import ThreadPoolExecutor


class Observer:
    def __init__(self, n, m, firefly_host="localhost"):
        self.n = n
        self.m = m
        self.firefly_host = firefly_host
        self.phases = [0] * (n * m)
        self.running = True  # Kontroll-Flag für das Beenden
        self.executor = ThreadPoolExecutor(max_workers=10)  # Thread-Pool für parallele Abfragen
        self.latencies = []  # Liste zur Speicherung der Latenzen
        self.latency_lock = Lock()  # Lock für thread-sicheren Zugriff auf die Latenzliste

    def fetch_phases(self):
        def query_firefly(i):
            try:
                start_time = time.time()  # Startzeit der Anfrage
                transport = TSocket.TSocket(self.firefly_host, 5001 + i)
                transport = TTransport.TBufferedTransport(transport)
                protocol = TBinaryProtocol.TBinaryProtocol(transport)
                client = FireflyService.Client(protocol)

                transport.open()
                response = client.getPhase(i)
                end_time = time.time()  # Endzeit der Antwort
                latency = (end_time - start_time) * 1000  # Latenz in Millisekunden

                # Speichere die Latenz thread-sicher
                with self.latency_lock:
                    self.latencies.append(latency)

                self.phases[i] = response.phase  # Korrigierter Zugriff
                transport.close()
            except Exception as e:
                print(f"Could not connect to Firefly {i}: {e}")

        while self.running:
            # Parallele Abfragen mit Thread-Pool
            futures = [self.executor.submit(query_firefly, i) for i in range(self.n * self.m)]
            for future in futures:
                future.result()  # Warten, bis alle Abfragen abgeschlossen sind
            time.sleep(0.5)

    def calculate_and_print_latency_stats(self):
        """Berechnet und gibt die Latenzstatistiken aus."""
        while self.running:
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
        root = tk.Tk()
        root.title("Firefly Observer")

        canvas = tk.Canvas(root, width=self.m * 50, height=self.n * 50)
        canvas.pack()

        rectangles = [[None for _ in range(self.m)] for _ in range(self.n)]
        for i in range(self.n):
            for j in range(self.m):
                x0, y0 = (j * 50, i * 50)
                x1, y1 = (x0 + 50, y0 + 50)
                rectangles[i][j] = canvas.create_rectangle(x0, y0, x1, y1, fill='black')

        def update_gui():
            if self.running:
                for i in range(self.n):
                    for j in range(self.m):
                        idx = i * self.m + j
                        phase = self.phases[idx]
                        color = int((math.sin(phase) + 1) * 127.5)
                        canvas.itemconfig(rectangles[i][j], fill=f'#{color:02x}{color:02x}{color:02x}')
                root.after(500, update_gui)

        def on_close():
            """Beenden des Observers."""
            self.running = False
            self.executor.shutdown(wait=False)  # Thread-Pool schließen
            root.destroy()

        root.protocol("WM_DELETE_WINDOW", on_close)  # Schließen-Handler hinzufügen
        update_gui()
        root.mainloop()

    def start(self):
        Thread(target=self.fetch_phases, daemon=True).start()
        Thread(target=self.calculate_and_print_latency_stats, daemon=True).start()
        self.visualize()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Firefly Observer")
    parser.add_argument("--n", type=int, required=True, help="Anzahl der Zeilen")
    parser.add_argument("--m", type=int, required=True, help="Anzahl der Spalten")
    parser.add_argument("--firefly-host", type=str, default="localhost", help="Host-Adresse der Fireflies")
    args = parser.parse_args()

    observer = Observer(args.n, args.m, firefly_host=args.firefly_host)
    observer.start()
