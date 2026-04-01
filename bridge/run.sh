#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo ".venv not found. Run ./setup-venv.sh first."
  exit 1
fi

if [ -z "$OLLAMA_MODEL" ]; then
  echo "OLLAMA_MODEL is not set. Example: OLLAMA_MODEL=qwen3.5:9b LOG_LEVEL=DEBUG ./run.sh"
  exit 1
fi

echo "Pulling Ollama model: $OLLAMA_MODEL"
ollama pull "$OLLAMA_MODEL"

# Add --reload for hot reloading during development
.venv/bin/python -m uvicorn src.server:app --host 127.0.0.1 --port 8080 --reload
