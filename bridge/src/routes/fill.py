import json
import re

from fastapi import APIRouter, HTTPException

from src.claude import run_claude
from src.log import logger
from src.models import FillRequest
from src.routes import session

router = APIRouter()


@router.post("/fill")
def fill(body: FillRequest):
    logger.debug(f"Request — {len(body.elements)} elements")
    if not session.session_id:
        raise HTTPException(503, "Session not initialized")
    if not body.elements:
        raise HTTPException(400, "Missing elements")

    prompt = f"""Fill out this job application form using the resume and materials you already have.

PAGE CONTENT:
{body.pageText[:4000]}

FORM ELEMENTS (use id or name to target each field):
{json.dumps(body.elements, indent=2)}

Return ONLY a JSON array. Each item: {{"id": "...", "name": "...", "value": "..."}}
- Use "id" if the element has one, else use "name"
- For dropdowns showing "Select One", pick the exact matching option text
- Skip fields where info is not in the resume (empty value)
- Output ONLY the JSON array, no explanation"""

    try:
        logger.info(f"Asking Claude for {len(body.elements)} elements (session {session.session_id})...")
        response, _ = run_claude(prompt, session_id=session.session_id)
        logger.debug(f"Claude raw response: {response}")
        match = re.search(r"\[[\s\S]*\]", response)
        if not match:
            raise ValueError("No JSON array in response: " + response[:200])
        fills = json.loads(match.group())
        filled = sum(1 for f in fills if f.get("value"))
        logger.info(f"Returning {filled} fills.")
        return {"fills": fills}
    except Exception as e:
        logger.error(f"Fill failed: {e}")
        raise HTTPException(500, str(e))
