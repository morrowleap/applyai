import json
import re

from fastapi import APIRouter, HTTPException

from src.claude import run_claude
from src.logger import logger
from src.models import ScoreRequest
from src import state

router = APIRouter()


@router.get("/keyword")
def generate_keyword():
    if not state.session_id:
        raise HTTPException(503, "Session not initialized")

    prompt = """Based on my resume (which you already have), generate ONE job search keyword or short phrase (2-5 words) that I should use on LinkedIn or job boards right now.

Requirements:
- Must be for individual contributor SOFTWARE ENGINEER roles only — NOT manager, lead, director, or VP titles
- Target the fintech and banking sector (payments, trading, core banking, lending — avoid the word "wealth management" as it surfaces non-engineering roles)
- Must reflect current (2025-2026) hiring demand in financial services engineering
- Must be specific enough to surface high-quality engineer matches
- Must be different from any keyword you have already suggested in this session
- Should combine my technical skills (Java, Spring Boot, microservices, Kafka, distributed systems) with a fintech domain

Return ONLY a JSON object:
{"keyword": "...", "rationale": "one sentence"}

Output ONLY the JSON object, no explanation."""

    try:
        logger.info(f"Generating job search keyword (session {state.session_id})...")
        response, _ = run_claude(prompt, session_id=state.session_id)
        logger.debug(f"Claude raw response: {response}")
        match = re.search(r"\{[\s\S]*\}", response)
        if not match:
            raise ValueError("No JSON object in response: " + response[:200])
        result = json.loads(match.group())
        return result
    except Exception as e:
        logger.error(f"Keyword generation failed: {e}")
        raise HTTPException(500, str(e))


@router.post("/score")
def score(body: ScoreRequest):
    if not state.session_id:
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
        logger.info(f"Scoring job: {body.title} at {body.company} (session {state.session_id})...")
        response, _ = run_claude(prompt, session_id=state.session_id)
        logger.debug(f"Claude raw response: {response}")
        match = re.search(r"\{[\s\S]*\}", response)
        if not match:
            raise ValueError("No JSON object in response: " + response[:200])
        result = json.loads(match.group())
        return result
    except Exception as e:
        logger.error(f"Score failed: {e}")
        raise HTTPException(500, str(e))
