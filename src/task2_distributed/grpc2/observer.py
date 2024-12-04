import grpc
import firefly_pb2
import firefly_pb2_grpc
from concurrent import futures
import tkinter as tk
import math
import argparse

class ObserverService(firefly_pb2_grpc.FireflyServicer):
    def __init__(self, n, m):
        self.phases = [0] * (n * m)
        self.n = n
        self.m = m

    def ReportState(self, request, context):
        """Empfängt den Zustand eines Firefly und aktualisiert ihn."""
        self.phases[request.id] = request.phase
        return firefly_pb2.Ack(message="State received")

    def get_phases(self):
        return self.phases

def start_observer_service(observer, port):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=None))
    firefly_pb2_grpc.add_FireflyServicer_to_server(observer, server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"Observer running on port {port}...")
    return server

def visualize(observer):
    n, m = observer.n, observer.m
    root = tk.Tk()
    canvas = tk.Canvas(root, width=m * 50, height=n * 50)
    canvas.pack()

    rectangles = [[None for _ in range(m)] for _ in range(n)]
    for i in range(n):
        for j in range(m):
            x0, y0 = (j * 50, i * 50)
            x1, y1 = (x0 + 50, y0 + 50)
            rectangles[i][j] = canvas.create_rectangle(x0, y0, x1, y1, fill='black')

    def update_gui():
        phases = observer.get_phases()
        for i in range(n):
            for j in range(m):
                idx = i * m + j
                phase = phases[idx]
                color = int((math.sin(phase) + 1) * 127.5)
                canvas.itemconfig(rectangles[i][j], fill=f'#{color:02x}{color:02x}{color:02x}')
        root.after(100, update_gui)

    update_gui()
    root.mainloop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Observer Process")
    parser.add_argument("--n", type=int, required=True, help="Anzahl der Zeilen")
    parser.add_argument("--m", type=int, required=True, help="Anzahl der Spalten")
    parser.add_argument("--port", type=int, default=5000, help="Port des Observers (Standard: 5000)")
    args = parser.parse_args()

    observer = ObserverService(args.n, args.m)
    server = start_observer_service(observer, args.port)
    visualize(observer)
