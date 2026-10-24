#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
fi

export PYTHONPATH="$PROJECT_ROOT/src:$PYTHONPATH"

echo "=== Launching Beyond 80 — Agent Control Center ==="
echo "Access the Control Center at: http://localhost:8000"
echo "API Docs at: http://localhost:8000/docs"

exec uvicorn videoautomater.server.app:app --host 0.0.0.0 --port 8000 --reload
