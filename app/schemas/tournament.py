from pydantic import BaseModel

class Tournament(BaseModel):
    id: str
    name: str

    class Config: 
        from_attributes = True