from pydantic import BaseModel

class Tournament(BaseModel):
    id: int
    name: str

    class Config: 
        from_attributes = True