import grpc
import fireflys_pb2
import fireflys_pb2_grpc
from concurrent import futures
import time
import math
import random
import signal
from multiprocessing import Value

# Globales Flag zum Beenden
RUNNING = Value('b', True)

class FireflyService(fireflys_pb2_grpc.FireflyServicer):
    def __init__(self, phase, id):
        self.phase = phase
        self.id = id

    def GetPhase(self, request, context):
        """Gibt die aktuelle Phase des Glühwürmchens zurück."""
        return fireflys_pb2.PhaseResponse(phase=self.phase)

def serve(port, phase, id):
    """Startet den gRPC-Server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    fireflys_pb2_grpc.add_FireflyServicer_to_server(FireflyService(phase, id), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    print(f"[Firefly {id}] Server running on port {port}...")
    return server

def firefly_client(id, neighbors, phase, omega, k):
    """Die Logik des Glühwürmchens."""
    while RUNNING.value:
        new_phase = phase
        for neighbor in neighbors:
            try:
                with grpc.insecure_channel(neighbor) as channel:
                    stub = fireflys_pb2_grpc.FireflyStub(channel)
                    response = stub.GetPhase(fireflys_pb2.PhaseRequest(id=id))
                    print(f"[Firefly {id}] Received phase={response.phase} from {neighbor}")
                    new_phase += k * math.sin(response.phase - phase)
            except grpc.RpcError as e:
                print(f"[Firefly {id}] Error communicating with {neighbor}: {e}")

        # Update eigene Phase
        phase = (phase + omega + new_phase) % (2 * math.pi)
        time.sleep(0.1)  # Simulationsschritt

def handle_signal(signal, frame):
    """Signalhandler zum Beenden."""
    RUNNING.value = False

signal.signal(signal.SIGTERM, handle_signal)
signal.signal(signal.SIGINT, handle_signal)

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Firefly Process")
    parser.add_argument("--n", type=int, required=True, help="Anzahl der Zeilen (Höhe des Gitters)")
    parser.add_argument("--m", type=int, required=True, help="Anzahl der Spalten (Breite des Gitters)")
    parser.add_argument("--id", type=int, required=True, help="ID des Glühwürmchens")
    parser.add_argument("--k", type=float, default=0.1, help="Kopplungsstärke (Standard: 0.1)")
    parser.add_argument("--omega", type=float, default=0.75, help="Natürliche Frequenz (Standard: 0.75)")
    args = parser.parse_args()

    # Initialisiere Phase
    phase = random.uniform(0, 2 * math.pi)

    # Port und Nachbarn berechnen
    port = 5001 + args.id
    neighbors = []
    n, m = args.n, args.m
    row, col = divmod(args.id, m)
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx != 0 or dy != 0:
                neighbor_row = (row + dx + n) % n
                neighbor_col = (col + dy + m) % m
                neighbor_id = neighbor_row * m + neighbor_col
                neighbors.append(f"localhost:{5001 + neighbor_id}")

    print(f"[Firefly {args.id}] Neighbors: {neighbors}")

    # Starte Server und Client
    server = serve(port, phase, args.id)
    firefly_client(args.id, neighbors, phase, args.omega, args.k)

    # Beende den Server
    server.stop(0)
    print(f"[Firefly {args.id}] Process terminated.")
