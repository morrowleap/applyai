from fastapi import APIRouter

from src.routes import session  # noqa: F401 — re-exported for server.py
from src.routes.fill import router as fill_router
from src.routes.health import router as health_router
from src.routes.score import router as score_router

router = APIRouter()
router.include_router(health_router)
router.include_router(fill_router)
router.include_router(score_router)
