from pydantic import BaseModel


class FillRequest(BaseModel):
    pageText: str = ""
    elements: list[dict] = []
    jobContext: str = ""


class ScoreRequest(BaseModel):
    title: str
    company: str
    description: str
