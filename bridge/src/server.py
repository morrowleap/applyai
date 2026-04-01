from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src import routes, state
from src.loader import RESOURCES_DIR, load_resources
from src.logger import logger


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Loading resources...")
    resources = load_resources()
    if not resources:
        raise RuntimeError(f"No readable files found in {RESOURCES_DIR}")
    state.resources = resources
    logger.info("Resources loaded. Ready.")
    yield
    logger.info("Shutting down.")


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(routes.router)
