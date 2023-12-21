from pydantic import BaseModel

class PlayerStat(BaseModel):
    name: str
    sg_total: float
    sg_ttg: float
    sg_ott: float
    sg_apr: float
    sg_atg: float
    sg_putt: float

    class Config: 
        from_attributes = True