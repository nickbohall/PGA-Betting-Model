from pydantic import BaseModel

class Master(BaseModel):
    year: int
    tourney_id: str
    tournament_name: str
    course_name: str
    player_name: str
    player_id: str
    finish: int
    score: int
    sg_total: float
    sg_ttg: float
    sg_ott: float
    sg_apr: float
    sg_atg: float
    sg_putt: float

    class Config: 
        from_attributes = True