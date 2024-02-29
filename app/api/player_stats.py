from typing  import Optional, List

import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.db_setup import get_db
from app.schemas.player_stats import PlayerStat as PlayerStatSchema
from app.crud.player_stats import add_player_stats, get_player_stats

router = fastapi.APIRouter()

db_dependency = Depends(get_db)

@router.get("/player_stats", response_model=List[PlayerStatSchema])
async def get_player_stats_from_db(db: Session = db_dependency, skip: int = 0, limit: int = 300):
    db_player_stats = get_player_stats(db)
    if not db_player_stats:  # Check if the list is empty or None
        raise HTTPException(status_code=404, detail="No player stats found")
    return db_player_stats 

@router.post("/player_stats", response_model=PlayerStatSchema, status_code=201)
async def add_player_stats_to_db(db: Session = db_dependency):
    player_stats = add_player_stats(db=db)
    if not player_stats:  # Check if the list is empty or None
        raise HTTPException(status_code=404, detail="No players found")
    return player_stats 

