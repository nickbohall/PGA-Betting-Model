from pydantic import BaseModel
from typing import Optional

class Master(BaseModel):
    year: int
    tourney_id: str
    tournament_name: str
    course_name: Optional[str]
    player_name: str
    player_id: str
    finish: Optional[int] 
    score: Optional[int] 
    sg_total: Optional[float] 
    sg_ttg: Optional[float]  
    sg_ott: Optional[float]  
    sg_apr: Optional[float]  
    sg_atg: Optional[float]  
    sg_putt: Optional[float]  
    odds: Optional[int] 

    class Config: 
        from_attributes = True