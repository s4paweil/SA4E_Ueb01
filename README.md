# SA4E_Ueb01

SA4E, Übungsbla/ 1, Winter 2024 von Patrick Weil (s4paweil@uni-trier.de)

Dieses Projekt implementiert die Synchronisation von Glühwürmchen über drei verschiedene Ansätze:
1. **Monolithische Lösung (Aufgabe 1)**.
2. **Verteilte Lösung mit gRPC (Aufgabe 2.1)**.
3. **Verteilte Lösung mit Apache Thrift (Aufgabe 2.2)**.

## Voraussetzungen

- **Python-Version**: 3.8 oder neuer
- Abhängigkeiten werden über `pip` installiert (siehe `requirements.txt`).

---

## Anleitung

### **1. Monolithische Lösung (Aufgabe 1)**
Die monolithische Lösung befindet sich unter: `./src/task1_monolith/`

#### Starten
```console
python task1_monolith.py <n> <m> [-k <K>] [-o <OMEGA>]
```
**Argumente:**
- `n`: Anzahl Reihen
- `m`: Anzahl Spalten
- `-k`: Kopplungsstärke (default: 0.1) - optional
- `-o`: Omega, Natürliche Frequenz (default: 0.75) - optional

**Beispiele:**
```console
python task1_monolith.py 10 10
```
```console
python task1_monolith.py 10 10 -k 0.75 -o 0.33
```

### **Aufgabe 2: Verteilte Systeme**
Zur Verwendung von gRPC bzw. Thrift werden einige Python Pakete benötigt, die in `requirements.txt` enthalten sind. Die Pakete können via `pip` installiert werden.
```console
pip install -r requirements.txt
```

### **2.1 Verteilte Lösung mit gRPC (Aufgabe 2)**
Die verteilte Lösung mit gRPC befindet sich unter: `./src/task2_distributed/grpc/`

#### Starten
Zum Starten muss zunächst der Observer und anschließend die Glühwürmchen über ein bash-Skript gestartet werden.

**1. Starten des Observers**
```console
python observer.py --n <n> --m <m> [--firefly-host <ip>]
```
**Argumente:**
- `n`: Anzahl Reihen
- `m`: Anzahl Spalten
- `--firefly-host`: IP-Adresse des Rechners auf dem die Glühwürmchen laufen (default: localhost) - optional

**2. Starten der Glühwürmchen**
```console
bash start_fireflys.sh -n <rows> -m <cols> [-k <K>] [-o <OMEGA>]
```
**Argumente:**
- `n`: Anzahl Reihen
- `m`: Anzahl Spalten
- `-k`: Kopplungsstärke (default: 0.1) - optional
- `-o`: Omega, Natürliche Frequenz (default: 0.75) - optional


**Beispiele:**
```console
python observer.py --n 10 --m 10
bash start_fireflys.sh -n 10 -m 10
```
```console
python observer.py --n 5 --m 5 --firefly-host 168.192.2.110
bash start_fireflys.sh -n 5 -m 5 -k 0.75 -o 0.33
```

### **2.2 Verteilte Lösung mit Apache Thrift (Aufgabe 2)**
Die verteilte Lösung mit Apache Thrift befindet sich unter: `./src/task2_distributed/thrift/`

#### Starten
Zum Starten muss zunächst der Observer und anschließend die Glühwürmchen über ein bash-Skript gestartet werden.

**1. Starten des Observers**
```console
python observer.py --n <n> --m <m> [--firefly-host <ip>]
```
**Argumente:**
- `n`: Anzahl Reihen
- `m`: Anzahl Spalten
- `--firefly-host`: IP-Adresse des Rechners auf dem die Glühwürmchen laufen (default: localhost) - optional

**2. Starten der Glühwürmchen**
```console
bash start_fireflys.sh -n <rows> -m <cols> [-k <K>] [-o <OMEGA>]
```
**Argumente:**
- `n`: Anzahl Reihen
- `m`: Anzahl Spalten
- `-k`: Kopplungsstärke (default: 0.1) - optional
- `-o`: Omega, Natürliche Frequenz (default: 0.75) - optional


**Beispiele:**
```console
python observer.py --n 10 --m 10
bash start_fireflys.sh -n 10 -m 10
```
```console
python observer.py --n 5 --m 5 --firefly-host 168.192.2.110
bash start_fireflys.sh -n 5 -m 5 -k 0.75 -o 0.33
```
