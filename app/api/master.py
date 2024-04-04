from typing  import Optional, List

import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

# Local Imports
from app.db.db_setup import get_db
from app.schemas.master import Master as MasterSchema 
from app.crud.master import *

from app.models.player import Player

router = fastapi.APIRouter()

db_dependency = Depends(get_db)

@router.get("/get_master", response_model=List[MasterSchema])
async def read_master_from_db(db: Session = db_dependency, limit: int=300):
    db_masters = get_masters_table(db)
    if not db_masters:  # Check if the list is empty or None
        raise HTTPException(status_code=404, detail="No masters found")
    return db_masters 

@router.post("/master/add_tourney{tournament_name}", response_model=MasterSchema, status_code=201)
async def add_master_to_db(tournament_name: str, db: Session = db_dependency):
    return add_new_tourney_to_master(tournament_name=tournament_name, db=db) or None

@router.patch("/master/add_tourney_SG{tournament_name}/{year}/",)
async def update_sg_stats_to_db(tournament_name: str, year: str, db: Session = db_dependency):
    return update_sg_stats(tournament_name=tournament_name, year=int(year), db=db)

@router.post("/master/add_historical_data", response_model=MasterSchema, status_code=201)
async def add_historical_data_to_master(db: Session = db_dependency):
    return get_historical_data_from_csv(db=db)

@router.patch("/master/add_tourney_finishes{tournament_name}/{year}/",)
async def add_tourney_finishes(tournament_name: str, year: str, db: Session = db_dependency):
    return add_tourney_finishes_to_master(tournament_name=tournament_name, year=int(year), db=db)

# Just for testing shit
@router.get("/test")
async def test_stuff(db: Session = db_dependency):
    return db.query(Player).filter(Player.id == "01226").first().name