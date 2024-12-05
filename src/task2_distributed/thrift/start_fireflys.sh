#!/bin/bash

# Standardwerte
DEFAULT_K=0.1
DEFAULT_OMEGA=0.75

# Argumente parsen
while getopts "n:m:k:o:" opt; do
  case $opt in
    n) n=$OPTARG ;;
    m) m=$OPTARG ;;
    k) k=$OPTARG ;;
    o) omega=$OPTARG ;;
    *) echo "Usage: $0 -n <rows> -m <cols> [-k <K>] [-o <OMEGA>]" >&2
       exit 1 ;;
  esac
done

# Überprüfen, ob die erforderlichen Argumente gesetzt sind
if [ -z "$n" ] || [ -z "$m" ]; then
  echo "Error: You must specify -n and -m." >&2
  exit 1
fi

# Standardwerte setzen
k=${k:-$DEFAULT_K}
omega=${omega:-$DEFAULT_OMEGA}

# Starte die Glühwürmchen
total=$((n * m))
pids=()
for id in $(seq 0 $((total - 1))); do
  echo "Starting Firefly $id..."
  python3 fireflys.py --n "$n" --m "$m" --id "$id" --k "$k" --omega "$omega" &
  pids+=($!)
done

# Warten auf Benutzereingabe zum Beenden
echo "Fireflies started. Press [Enter] to stop."
read -r

# Beende alle Prozesse sicher
echo "Stopping Fireflies..."
for pid in "${pids[@]}"; do
  if ps -p "$pid" > /dev/null; then
    echo "Stopping process $pid..."
    kill "$pid"
    wait "$pid" 2>/dev/null  # Warte, bis der Prozess beendet ist
  else
    echo "Process $pid is not running."
  fi
done

echo "All Fireflies stopped."
