import logging
import os
from datetime import datetime
from pathlib import Path

# Log level hierarchy (each level shows itself and everything above):
#   DEBUG < INFO < WARNING < ERROR
#
# Usage:
#   LOG_LEVEL=DEBUG ./run.sh    → default, shows everything
#   LOG_LEVEL=INFO ./run.sh     → hides DEBUG
#   LOG_LEVEL=WARNING ./run.sh  → hides DEBUG and INFO
#   LOG_LEVEL=ERROR ./run.sh    → errors only

LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG").upper()

LOGS_DIR = Path(__file__).resolve().parent.parent / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOG_FILE = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

handler = logging.FileHandler(LOG_FILE)
handler.setFormatter(logging.Formatter(
    fmt="%(asctime)s [%(levelname)s] %(module)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
))

logger = logging.getLogger("job-applier-bridge")
logger.setLevel(LOG_LEVEL)
logger.addHandler(handler)
