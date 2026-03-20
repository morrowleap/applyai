from fastapi import APIRouter

from src.routes.health import router as health_router
from src.routes.job_research import router as job_research_router

router = APIRouter()
router.include_router(health_router)
router.include_router(job_research_router)
