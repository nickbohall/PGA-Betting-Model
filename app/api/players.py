from typing  import Optional, List

import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.db_setup import get_db
from app.schemas.player import PlayerBase as PlayerSchema 
from app.crud.players import get_player, get_player_by_name, get_players, add_players

router = fastapi.APIRouter()

db_dependency = Depends(get_db)

@router.get("/players", response_model=List[PlayerSchema])
async def read_players(db: Session = db_dependency, skip: int = 0, limit: int = 300):
    db_players = get_players(db)
    if not db_players:  # Check if the list is empty or None
        raise HTTPException(status_code=404, detail="No players found")
    return db_players 

@router.post("/players", response_model=PlayerSchema, status_code=201)
async def add_players_to_db(db: Session = db_dependency):
    return add_players(db=db)