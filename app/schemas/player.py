from pydantic import BaseModel
from datetime import datetime

class PlayerBase(BaseModel):
    id: str
    name: str
    nationality: str

class PlayerCreate(PlayerBase):
    ...
    

class Player(PlayerBase):
    ...