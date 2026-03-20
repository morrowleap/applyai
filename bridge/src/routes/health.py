from fastapi import APIRouter

from src import state

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "session_id": state.session_id}
