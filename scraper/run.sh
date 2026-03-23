#!/bin/bash
set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo ".venv not found. Run ./setup-venv.sh first."
  exit 1
fi

.venv/bin/python find.py "$@"
