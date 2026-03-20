#!/usr/bin/env bash
set -e

cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo ".venv not found. Run ./setup-venv.sh first."
  exit 1
fi

# Add --reload for hot reloading during development
.venv/bin/python -m uvicorn src.server:app --host 127.0.0.1 --port 8080 --reload
