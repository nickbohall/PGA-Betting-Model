from typing  import Optional, List

import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.db_setup import get_db
from app.schemas.player import Player as playerSchema
from app.crud.players import get_player, get_player_by_name, get_players

router = fastapi.APIRouter()

db_dependency = Depends(get_db)

@router.get("/players", response_model=List[playerSchema])
async def read_players(db: Session = db_dependency, skip: int = 0, limit: int = 300):
    players = get_players(db, skip=skip, limit=limit)
    return players

# @router.post("/players")
# async def add_players(player: SchemaPlayer, db: db_dependency:
#     player_info = PgaScrape().get_player_info()
#     for player in player_info:
#         print(player)
#         ind_player = Player(id=player["id"], name=player["name"], nationality=player["nationality"])
#         try: 
#             db.add(ind_player)
#         except sqlalchemy.exc.IntegrityError as sqla_error:
#             pass
#     db.commit()

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