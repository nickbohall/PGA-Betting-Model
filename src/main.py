# Package Imports
from fastapi import FastAPI, HTTPException, Depends
from typing import List, Annotated
from sqlalchemy.orm import Session
from icecream import ic

# Error Handling
from psycopg2 import errors
import sqlalchemy

# Local Inports
from .models import Player, Tournament, Schedule
from .schema import Player as SchemaPlayer, Tournament as SchemaTournament, Schedule as SchemaSchedule
from .database import engine, SessionLocal, Base
from .controller import PgaScrape

app = FastAPI()
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally: db.close()

db_dependency = Annotated[Session, Depends(get_db)]

@app.get("/")
async def root():
    return {"message": "This is a PGA Betting Model"}

@app.post("/players")
async def add_players(player: SchemaPlayer, db: db_dependency):
    player_info = PgaScrape().get_player_info()
    for player in player_info:
        print(player)
        ind_player = Player(id=player["id"], name=player["name"], nationality=player["nationality"])
        try: 
            db.add(ind_player)
        except sqlalchemy.exc.IntegrityError as sqla_error:
            pass
    db.commit()

@app.get("/players")
def get_players(db: db_dependency):
    result = db.query(Player).all()
    if not result:
        raise HTTPException(status_code=404, detail='players not found')
    return result
