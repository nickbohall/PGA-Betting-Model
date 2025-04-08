from pydantic import BaseModel, Field
from typing import Optional

class PlayerStat(BaseModel):
    name: str
    id: str
    sg_total: Optional[float] = Field(default=0.0)
    sg_ttg: Optional[float] = Field(default=0.0)
    sg_ott: Optional[float] = Field(default=0.0)
    sg_apr: Optional[float] = Field(default=0.0)
    sg_atg: Optional[float] = Field(default=0.0)
    sg_putt: Optional[float] = Field(default=0.0)

    class Config: 
        from_attributes = True