import requests

BRIDGE_URL = "http://localhost:8080/score"


def score_job(title: str, company: str, description: str) -> dict:
    """Score a job against the resume via bridge. Returns score dict or fallback."""
    try:
        resp = requests.post(
            BRIDGE_URL,
            json={"title": title, "company": company, "description": description},
            timeout=60,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        return {
            "score": 0,
            "reason": f"bridge unavailable: {e}",
            "skills_match": [],
            "missing": [],
        }
