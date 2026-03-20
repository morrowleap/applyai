from pathlib import Path

from src.log import logger

BASE_DIR = Path(__file__).resolve().parent.parent
RESOURCES_DIR = BASE_DIR / "resources"
SKIP_EXTENSIONS = {".pdf"}


def load_resources() -> str:
    """Read all text-readable files from resources/ and return combined content."""
    parts = []
    for path in sorted(RESOURCES_DIR.iterdir()):
        if path.suffix.lower() in SKIP_EXTENSIONS or not path.is_file():
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
            parts.append(f"=== {path.name} ===\n{content.strip()}")
            logger.debug(f"Loaded resource: {path.name}")
        except Exception as e:
            logger.warning(f"Could not read {path.name}: {e}")
    return "\n\n".join(parts)
