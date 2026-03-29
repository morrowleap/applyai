from fastapi import APIRouter

from src import state

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "resources_loaded": state.resources is not None}
