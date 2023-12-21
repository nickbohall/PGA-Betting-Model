from typing  import Optional, List

import fastapi
from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

# Local Imports
from app.db.db_setup import get_db
from app.schemas.schedule import Schedule as ScheduleSchema 
from app.crud.schedule import get_schedule, get_schedules, add_schedules

router = fastapi.APIRouter()

db_dependency = Depends(get_db)

@router.get("/schedules", response_model=List[ScheduleSchema])
async def read_schedules_from_db(db: Session = db_dependency, skip: int = 0, limit: int = 300):
    db_schedules = get_schedules(db)
    if not db_schedules:  # Check if the list is empty or None
        raise HTTPException(status_code=404, detail="No schedules found")
    return db_schedules 

@router.post("/schedules", response_model=ScheduleSchema, status_code=201)
async def add_schedules_to_db(db: Session = db_dependency):
    return add_schedules(db=db)