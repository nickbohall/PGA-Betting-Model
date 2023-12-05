from pydantic import BaseModel

class Schedule(BaseModel):
    year: int
    finish: int

    class Config: 
        from_attributes = True