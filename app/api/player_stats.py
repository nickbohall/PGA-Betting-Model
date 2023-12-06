from typing  import Optional, List

import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.db_setup import get_db
from app.schemas.player import Player as playerSchema
from app.crud.player_stats import add_player_stats

router = fastapi.APIRouter()

db_dependency = Depends(get_db)

@router.post("/player_stats", response_model=playerSchema, status_code=201)
async def add_player_stats_to_db(db: Session = db_dependency):
    player_stats = add_player_stats(db=db)
    if not player_stats:  # Check if the list is empty or None
        raise HTTPException(status_code=404, detail="No players found")
    return player_stats 