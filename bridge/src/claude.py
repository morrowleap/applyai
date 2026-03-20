import json
import subprocess
from pathlib import Path

from src.log import logger

BACKEND_DIR = Path(__file__).resolve().parent.parent


def run_claude(prompt: str, session_id: str | None = None) -> tuple[str, str]:
    """Call Claude CLI, return (result_text, session_id)."""
    cmd = ["claude", "-p", "--output-format", "json"]
    if session_id:
        cmd += ["--resume", session_id]
    logger.debug(f"Running Claude CLI (session={session_id})")
    result = subprocess.run(cmd, input=prompt, capture_output=True, text=True, timeout=120, cwd=BACKEND_DIR)
    if result.returncode != 0 and not result.stdout:
        error = result.stderr or f"Claude CLI exited with code {result.returncode}"
        logger.error(f"Claude CLI failed: {error}")
        raise RuntimeError(error)
    data = json.loads(result.stdout)
    return data["result"], data["session_id"]
