from pydantic import BaseModel

class Player(BaseModel):
    id: str
    name: str
    nationality: str
    
    class Config: 
        from_attributes = True

class PlayerStats(BaseModel):
    id: str
    sg_total: int
    sg_ttg: int
    sg_ott: int
    sg_apr: int
    sg_atg: int
    sg_putt: int

    class Config: 
        from_attributes = True