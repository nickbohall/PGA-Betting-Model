from pydantic import BaseModel

class Master(BaseModel):
    year: int
    tourney_id: str
    tournament_name: str
    course_name: str
    player_name: str
    player_id: str
    finish: int = None
    score: int = None
    sg_total: float = None
    sg_ttg: float = None
    sg_ott: float = None
    sg_apr: float = None
    sg_atg: float = None
    sg_putt: float = None
    odds: int

    class Config: 
        from_attributes = True