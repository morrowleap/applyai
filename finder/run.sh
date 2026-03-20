#!/bin/bash
set -e
cd "$(dirname "$0")"

if [ ! -d ".venv" ]; then
  echo "Setting up venv..."
  ./setup-venv.sh
fi

source .venv/bin/activate
python find.py "$@"
