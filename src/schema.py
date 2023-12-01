from pydantic import BaseModel

class Player(BaseModel):
    id: int
    name: str
    nationality: str

class Tournament(BaseModel):
    id: int
    name: str

class Schedule(BaseModel):
    year: int
    finish: int
