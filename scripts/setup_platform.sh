#!/usr/bin/env bash
set -e

echo "=== Beyond 80 — Platform Setup ==="

# Check Python version
python3 --version

# Setup virtual environment if not present
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Installing platform dependencies..."
pip install --upgrade pip
pip install fastapi uvicorn[standard] aiofiles starlette edge-tts pillow numpy soundfile pydantic pytest

echo "Setting up output directories..."
mkdir -p output/platform_db output/episode_001

echo "Setup complete. Run ./scripts/run_platform.sh to launch the Agent Control Center."
