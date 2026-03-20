import json
import re

from fastapi import APIRouter, HTTPException

from src.claude import run_claude
from src.log import logger
from src.models import ScoreRequest
from src.routes import session

router = APIRouter()


@router.post("/score")
def score(body: ScoreRequest):
    if not session.session_id:
        raise HTTPException(503, "Session not initialized")

    prompt = f"""Score this job posting for fit with my profile.

JOB TITLE: {body.title}
COMPANY: {body.company}
DESCRIPTION:
{body.description[:3000]}

Return ONLY a JSON object with these fields:
- score: integer 1-10 (10 = perfect fit)
- reason: one sentence explaining the score
- skills_match: list of matching skills from my resume
- missing: list of required skills I lack

Output ONLY the JSON object, no explanation."""

    try:
        logger.info(f"Scoring job: {body.title} at {body.company} (session {session.session_id})...")
        response, _ = run_claude(prompt, session_id=session.session_id)
        logger.debug(f"Claude raw response: {response}")
        match = re.search(r"\{[\s\S]*\}", response)
        if not match:
            raise ValueError("No JSON object in response: " + response[:200])
        result = json.loads(match.group())
        return result
    except Exception as e:
        logger.error(f"Score failed: {e}")
        raise HTTPException(500, str(e))
