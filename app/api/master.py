from typing  import Optional, List

import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

# Local Imports
from app.db.db_setup import get_db
from app.schemas.master import Master as MasterSchema 
from app.crud.master import get_historical_data_from_csv, get_masters_table, add_master_table, update_sg_stats

from app.models.player import Player

router = fastapi.APIRouter()

db_dependency = Depends(get_db)

@router.get("/master", response_model=List[MasterSchema])
async def read_master_from_db(db: Session = db_dependency, skip: int = 0, limit: int = 300):
    db_masters = get_masters_table(db)
    if not db_masters:  # Check if the list is empty or None
        raise HTTPException(status_code=404, detail="No masters found")
    return db_masters 

@router.post("/master", response_model=MasterSchema, status_code=201)
async def add_master_to_db(db: Session = db_dependency):
    return add_master_table(db=db)

@router.patch("/master/{tournament_name}/{year}/",)
async def update_sg_stats_to_db(tournament_name: str, year: str, db: Session = db_dependency):
    return update_sg_stats(tournament_name=tournament_name, year=int(year), db=db)

@router.post("/master/historical", response_model=MasterSchema, status_code=201)
async def add_historical_data_to_master(db: Session = db_dependency):
    return get_historical_data_from_csv(db=db)

# Just for testing shit
@router.get("/test")
async def test_stuff(db: Session = db_dependency):
    return db.query(Player).filter(Player.id == "01226").first().name