from fastapi import APIRouter

from src.routes import session

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok", "session_id": session.session_id}
