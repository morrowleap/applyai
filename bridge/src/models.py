from pydantic import BaseModel


class ScoreRequest(BaseModel):
    title: str
    description: str
    link: str
