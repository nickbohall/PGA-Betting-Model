from typing  import Optional, List

import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.db_setup import get_db
from app.schemas.tournament import Tournament as TournamentSchema 
from app.crud.tournaments import get_tournaments, add_tournaments

router = fastapi.APIRouter()

db_dependency = Depends(get_db)

@router.get("/tournaments", response_model=List[TournamentSchema])
async def read_tournaments_from_db(db: Session = db_dependency, skip: int = 0, limit: int = 300):
    db_tournaments = get_tournaments(db)
    if not db_tournaments:  # Check if the list is empty or None
        raise HTTPException(status_code=404, detail="No tournaments found")
    return db_tournaments 

@router.post("/tournaments", response_model=TournamentSchema, status_code=201)
async def add_tournaments_to_db(db: Session = db_dependency):
    return add_tournaments(db=db)