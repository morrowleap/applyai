from pydantic import BaseModel

class ScoreRequest(BaseModel):
    title: str
    company: str
    description: str
