from pydantic import BaseModel

class Tournament(BaseModel):

    tourney_name: str
    tourney_id: str
    course_name: str

    class Config: 
        from_attributes = True