import grpc
import firefly_pb2
import firefly_pb2_grpc
from concurrent import futures
import random
import math
import time
import argparse


class FireflyService(firefly_pb2_grpc.FireflyServicer):
    def __init__(self, id, phase, neighbors, observer_address):
        self.id = id
        self.phase = phase
        self.neighbors = neighbors
        self.observer_address = observer_address

    def SyncState(self, request, context):
        """Empfängt und verarbeitet den Zustand eines Nachbarn."""
        self.phase += K * math.sin(request.phase - self.phase)
        self.phase %= 2 * math.pi
        return firefly_pb2.FireflyState(id=self.id, phase=self.phase)

    def ReportState(self, request, context):
        """Empfängt Anfrage vom Observer (wird hier nicht aktiv genutzt)."""
        return firefly_pb2.Ack(message="State received")

    def run(self):
        """Simuliert die natürliche Entwicklung des Firefly."""
        while True:
            self.phase += OMEGA
            self.phase %= 2 * math.pi
            self.report_to_observer()
            time.sleep(0.1)

    def report_to_observer(self):
        """Sendet den aktuellen Zustand an den Observer."""
        try:
            with grpc.insecure_channel(self.observer_address) as channel:
                stub = firefly_pb2_grpc.FireflyStub(channel)
                stub.ReportState(firefly_pb2.FireflyState(id=self.id, phase=self.phase))
        except grpc.RpcError as e:
            print(f"Error reporting to observer: {e}")

def serve(id, neighbors, observer_address, port):
    """Startet den Firefly-Server."""
    phase = random.uniform(0, 2 * math.pi)
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    service = FireflyService(id, phase, neighbors, observer_address)
    firefly_pb2_grpc.add_FireflyServicer_to_server(service, server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"Firefly {id} running on port {port}...")
    service.run()

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Firefly Process")
    parser.add_argument("--id", type=int, required=True, help="Firefly ID")
    parser.add_argument("--neighbors", nargs="+", required=True, help="Neighbor addresses")
    parser.add_argument("--observer", type=str, required=True, help="Observer address")
    parser.add_argument("--port", type=int, required=True, help="Port to run on")
    parser.add_argument("--k", type=float, default=0.1, help="Kopplungsstärke (Standard: 0.1)")
    parser.add_argument("--omega", type=float, default=0.75, help="Natürliche Frequenz (Standard: 0.75)")
    parser.add_argument("--time", type=int, default=60, help="Laufzeit des Prozesses in Sekunden")
    args = parser.parse_args()

    # Setze K und OMEGA basierend auf den Argumenten
    global K, OMEGA
    K = args.k
    OMEGA = args.omega

    # Laufzeit des Prozesses
    start_time = time.time()
    end_time = start_time + args.time

    # Starten des Servers
    serve(args.id, args.neighbors, args.observer, args.port)

    # Überwachung der Laufzeit
    while time.time() < end_time:
        time.sleep(1)

    print(f"Firefly {args.id} beendet nach {args.time} Sekunden.")

