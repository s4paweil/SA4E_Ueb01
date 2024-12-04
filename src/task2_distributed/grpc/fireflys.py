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
    def __init__(self, shared_phase, id):
        self.shared_phase = shared_phase  # Verwende die geteilte Phase
        self.id = id

    def GetPhase(self, request, context):
        """Gibt die aktuelle Phase des Glühwürmchens zurück."""
        # print(f"Firefly {self.id} returning phase {self.shared_phase.value}")
        return fireflys_pb2.PhaseResponse(phase=self.shared_phase.value)

def serve(port, shared_phase, id):
    """Startet den gRPC-Server."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=2))
    fireflys_pb2_grpc.add_FireflyServicer_to_server(FireflyService(shared_phase, id), server)
    server.add_insecure_port(f"[::]:{port}")
    server.start()
    return server

def firefly_client(id, neighbors, shared_phase, omega, k):
    """Die Logik des Glühwürmchens."""
    retry_delay = 0.5  # Wartezeit (Sekunden) vor dem erneuten Versuch, wenn ein Nachbar nicht erreichbar ist
    retry_attempts = 3  # Maximale Anzahl an Wiederholungsversuchen pro Nachbar

    while RUNNING.value:
        # Initialisiere Phase-Berechnung
        neighbors_phase = 0
        neighbors_count = 0

        # Sammle Phasen aller Nachbarn
        for neighbor in neighbors:
            for attempt in range(retry_attempts):
                try:
                    with grpc.insecure_channel(neighbor) as channel:
                        stub = fireflys_pb2_grpc.FireflyStub(channel)
                        response = stub.GetPhase(fireflys_pb2.PhaseRequest(id=id))
                        neighbors_phase += response.phase
                        neighbors_count += 1
                        break  # Erfolgreich, keine weiteren Versuche nötig
                except grpc.RpcError:
                    if attempt < retry_attempts - 1:
                        time.sleep(retry_delay)  # Warte und versuche erneut
                    else:
                        pass

        # Berechne Durchschnittsphase der Nachbarn
        if neighbors_count > 0:
            average_phase = neighbors_phase / neighbors_count
        else:
            average_phase = 0  # Keine Nachbarn erreichbar

        # Update eigene Phase
        with shared_phase.get_lock():  # Sicherstellen, dass nur ein Prozess die Phase aktualisiert
            shared_phase.value = (shared_phase.value + omega + k * math.sin(average_phase - shared_phase.value)) % (2 * math.pi)

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
    shared_phase = Value("d", random.uniform(0, 2 * math.pi))  # Geteilte Phase

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

    # Starte Server und Client
    server = serve(port, shared_phase, args.id)
    firefly_client(args.id, neighbors, shared_phase, args.omega, args.k)

    # Beende den Server
    server.stop(0)
