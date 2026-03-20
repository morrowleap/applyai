from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src import routes, state
from src.claude import run_claude
from src.loader import RESOURCES_DIR, load_resources
from src.logger import logger

SESSION_DIR = Path.home() / ".claude" / "projects" / str(Path.cwd()).replace("/", "-")


def cleanup_sessions():
    if SESSION_DIR.exists():
        orphans = list(SESSION_DIR.glob("*.jsonl"))
        for f in orphans:
            f.unlink()
            logger.warning(f"Cleaned up orphaned session: {f.name}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    cleanup_sessions()
    logger.info("Loading resources and initializing Claude session...")
    resources = load_resources()
    if not resources:
        raise RuntimeError(f"No readable files found in {RESOURCES_DIR}")

    init_prompt = f"""You are a job application assistant. Below are my job application materials.
Read and remember them — you will use this information to fill out job application forms in follow-up requests.

{resources}

Acknowledge that you have read these materials and give a brief summary of who I am and my key skills."""

    result, state.session_id = run_claude(init_prompt)
    logger.info(f"Session ready: {state.session_id}")
    logger.debug(f"Claude init response: {result[:300]}")
    yield
    logger.info("Shutting down.")
    session_file = SESSION_DIR / f"{state.session_id}.jsonl"
    if session_file.exists():
        session_file.unlink()
        logger.info(f"Session {state.session_id} cleaned up at {session_file}")
    else:
        logger.warning(f"Session file not found for {state.session_id} at {session_file}")


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(routes.router)
