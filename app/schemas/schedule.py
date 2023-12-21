from pydantic import BaseModel

class Schedule(BaseModel):
    year: int
    tourney_id: str
    tournament_name: str
    player_name: str
    player_id: str
    finish: int
    score: int

    class Config: 
        from_attributes = True