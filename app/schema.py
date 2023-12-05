from pydantic import BaseModel

class Player(BaseModel):
    id: str
    name: str
    nationality: str

class Tournament(BaseModel):
    id: int
    name: str

class Schedule(BaseModel):
    year: int
    finish: int

class PlayerStats(BaseModel):
    id: str
    sg_total: int
    sg_ttg: int
    sg_ott: int
    sg_apr: int
    sg_atg: int
    sg_putt: int

