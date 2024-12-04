#!/bin/bash

# Standardwerte für K, OMEGA und Laufzeit
DEFAULT_K=0.1
DEFAULT_OMEGA=0.75
DEFAULT_TIME=60  # Standardlaufzeit in Sekunden

# Parse Arguments
while getopts "n:m:k:o:t:" opt; do
  case $opt in
    n) n=$OPTARG ;;
    m) m=$OPTARG ;;
    k) K=$OPTARG ;;
    o) OMEGA=$OPTARG ;;
    t) TIME=$OPTARG ;;
    *) echo "Usage: $0 -n <rows> -m <cols> [-k <K>] [-o <OMEGA>] [-t <time>]" >&2
       exit 1 ;;
  esac
done

# Überprüfen, ob n und m angegeben wurden
if [ -z "$n" ] || [ -z "$m" ]; then
  echo "Error: You must specify -n (rows) and -m (cols)." >&2
  exit 1
fi

# Setze Standardwerte für K, OMEGA und Laufzeit, falls nicht angegeben
K=${K:-$DEFAULT_K}
OMEGA=${OMEGA:-$DEFAULT_OMEGA}
TIME=${TIME:-$DEFAULT_TIME}

# Starten des Observers
echo "Starting observer with n=$n, m=$m..."
python3 observer.py --n "$n" --m "$m" &

# Kurze Wartezeit, damit der Observer zuerst startet
sleep 1

# Starten der Glühwürmchen
for ((i=0; i<n; i++)); do
  for ((j=0; j<m; j++)); do
    id=$((i * m + j))
    port=$((5001 + id))
    neighbors=""
    for dx in -1 0 1; do
      for dy in -1 0 1; do
        if [ $dx -ne 0 ] || [ $dy -ne 0 ]; then
          ni=$(((i + dx + n) % n))
          nj=$(((j + dy + m) % m))
          neighbor_port=$((5001 + ni * m + nj))
          neighbors="$neighbors localhost:$neighbor_port"
        fi
      done
    done
    echo "Starting Firefly $id on port $port with K=$K, OMEGA=$OMEGA, and TIME=$TIME..."
    python3 firefly.py --id "$id" --neighbors $neighbors --observer localhost:5000 --port "$port" --k "$K" --omega "$OMEGA" --time "$TIME" &
  done
done

echo "All processes started. Fireflies will run for $TIME seconds."