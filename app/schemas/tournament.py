from pydantic import BaseModel, Field
from typing import Optional

class Tournament(BaseModel):
    id: int | None = None
    tournament_name: str
    tournament_id: str
    course_name: str
    year: int | None = None
    tournament_date: str | None = None

    class Config:
        from_attributes = True
        populate_by_name = True