from gen_py.fireflys import FireflyService
from gen_py.fireflys.ttypes import PhaseResponse
from thrift.transport import TSocket, TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from multiprocessing import Value
import threading
import time
import math
import random
import argparse

# Globales Flag zum Beenden
RUNNING = Value('b', True)

class FireflyServiceHandler:
    def __init__(self, shared_phase, id):
        self.shared_phase = shared_phase
        self.id = id

    def getPhase(self, id):
        """Gibt die aktuelle Phase des Glühwürmchens zurück."""
        print(f"Firefly {self.id} returning phase {self.shared_phase.value}")
        return PhaseResponse(phase=self.shared_phase.value)  # Korrektes Thrift-Objekt zurückgeben


def start_server(port, shared_phase, id):
    """Startet den Thrift-Server."""
    handler = FireflyServiceHandler(shared_phase, id)
    processor = FireflyService.Processor(handler)
    transport = TSocket.TServerSocket(port=port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()

    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    print(f"Firefly {id} Server running on port {port}...")
    server.serve()


def firefly_client(id, neighbors, shared_phase, omega, k):
    """Die Logik des Glühwürmchens."""
    while RUNNING.value:
        neighbors_phase = 0
        neighbors_count = 0

        for neighbor in neighbors:
            try:
                transport = TSocket.TSocket(neighbor["host"], neighbor["port"])
                transport = TTransport.TBufferedTransport(transport)
                protocol = TBinaryProtocol.TBinaryProtocol(transport)
                client = FireflyService.Client(protocol)

                transport.open()
                response = client.getPhase(id)
                neighbors_phase += response.phase  # `response.phase` ist der Wert, nicht `response["phase"]`
                neighbors_count += 1
                transport.close()
            except Exception as e:
                print(f"Error connecting to neighbor {neighbor}: {e}")

        if neighbors_count > 0:
            average_phase = neighbors_phase / neighbors_count
        else:
            average_phase = 0

        with shared_phase.get_lock():
            shared_phase.value = (shared_phase.value + omega + k * math.sin(average_phase - shared_phase.value)) % (2 * math.pi)

        time.sleep(0.1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Firefly Process")
    parser.add_argument("--n", type=int, required=True, help="Anzahl der Zeilen (Höhe des Gitters)")
    parser.add_argument("--m", type=int, required=True, help="Anzahl der Spalten (Breite des Gitters)")
    parser.add_argument("--id", type=int, required=True, help="ID des Glühwürmchens")
    parser.add_argument("--k", type=float, default=0.1, help="Kopplungsstärke (Standard: 0.1)")
    parser.add_argument("--omega", type=float, default=0.75, help="Natürliche Frequenz (Standard: 0.75)")
    args = parser.parse_args()

    shared_phase = Value("d", random.uniform(0, 2 * math.pi))

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
                neighbors.append({"host": "localhost", "port": 5001 + neighbor_id})

    threading.Thread(target=start_server, args=(port, shared_phase, args.id), daemon=True).start()
    firefly_client(args.id, neighbors, shared_phase, args.omega, args.k)
