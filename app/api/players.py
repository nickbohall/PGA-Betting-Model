from typing  import Optional, List

import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.db_setup import get_db
from app.schemas.player import Player as playerSchema
from app.crud.players import get_player, get_player_by_name, get_players, add_players

router = fastapi.APIRouter()

db_dependency = Depends(get_db)

@router.get("/players", response_model=List[playerSchema])
async def read_players(db: Session = db_dependency, skip: int = 0, limit: int = 300):
    db_players = get_players(db, skip=skip, limit=limit)
    if db_players == None: 
        raise HTTPException(status_code=404, detail="User not found")
    return db_players

@router.post("/players", response_model=playerSchema, status_code=201)
async def add_players_to_db(db: Session = db_dependency):
    return add_players(db=db)

# @app.post("/player_stats")
# async def add_player_stats(player_stats: SchemaPlayerStats, db: db_dependency):
#     player_stats = PgaScrape().get_player_stats()
#     for player in player_stats:
#         print(player_stats)
#         ind_stats = PlayerStats(id=player["id"] )
#         try: 
#             db.add(ind_stats)
#         except sqlalchemy.exc.IntegrityError as sqla_error:
#             pass
#     db.commit()