import json
import re

from fastapi import APIRouter, HTTPException

from src.llm.ollama import run_ollama
from src.logger import logger
from src.models import ScoreRequest
from src import state

router = APIRouter()


@router.get("/keyword")
def generate_keyword():
    if not state.resources:
        raise HTTPException(503, "Resources not loaded")

    prompt = f"""Here are my job application materials:

{state.resources}

Based on my profile above, generate ONE job search keyword or short phrase (2-5 words) that I should use on LinkedIn or job boards right now.

Requirements:
- Must be for individual contributor SOFTWARE ENGINEER roles only — NOT manager, lead, director, or VP titles
- Target the fintech and banking sector (payments, trading, core banking, lending — avoid the word "wealth management" as it surfaces non-engineering roles)
- Must reflect current (2025-2026) hiring demand in financial services engineering
- Must be specific enough to surface high-quality engineer matches
- Should combine my technical skills (Java, Spring Boot, microservices, Kafka, distributed systems) with a fintech domain

Return ONLY a JSON object:
{{"keyword": "...", "rationale": "one sentence"}}

Output ONLY the JSON object, no explanation."""

    try:
        logger.info("Generating job search keyword...")
        response = run_ollama(prompt)
        logger.debug(f"LLM raw response: {response}")
        match = re.search(r"\{[\s\S]*\}", response)
        if not match:
            raise ValueError("No JSON object in response: " + response)
        result = json.loads(match.group())
        return result
    except Exception as e:
        logger.error(f"Keyword generation failed: {e}")
        raise HTTPException(500, str(e))


@router.post("/score")
def score(body: ScoreRequest):
    if not state.resources:
        raise HTTPException(503, "Resources not loaded")

    prompt = f"""Here are my job application materials:

{state.resources}

Score this job posting for fit with my profile.

JOB TITLE: {body.title}
DESCRIPTION:
{body.description}

Return ONLY a JSON object with these fields:
- score: integer 1-10 (10 = perfect fit)
- reason: one sentence explaining the score
- skills_match: list of matching skills from my resume
- missing: list of required skills I lack

Output ONLY the JSON object, no explanation."""

    try:
        logger.info(f"Scoring job: {body.title} | {body.link}")
        response = run_ollama(prompt)
        logger.debug(f"LLM raw response: {response}")
        match = re.search(r"\{[\s\S]*\}", response)
        if not match:
            raise ValueError("No JSON object in response: " + response)
        result = json.loads(match.group())
        return result
    except Exception as e:
        logger.error(f"Score failed: {e}")
        raise HTTPException(500, str(e))
