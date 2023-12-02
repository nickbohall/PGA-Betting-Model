from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
from sqlalchemy.orm import Session
import sqlalchemy

from .models import Player, Tournament, Schedule
from .schema import Player as SchemaPlayer, Tournament as SchemaTournament, Schedule as SchemaSchedule
from .database import engine, SessionLocal, Base
from .controller import PgaScrape

app = FastAPI()
Base.metadata.create_all(bind=engine)

pga_scrape = PgaScrape() # Calling the Scrape class to input into our APIs

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
    player_info = pga_scrape.get_player_info()
    for player in player_info:
        ind_player = Player(id=player["id"], name=player["name"], nationality=player["nationality"])
        print(ind_player)
        try: 
            db.add(ind_player)
        except sqlalchemy.exc.IntegrityError:
            pass
    db.commit()

@app.get("/players")
def get_players():
    result = db.query(Player).all()
    if not result:
        raise HTTPException(status_code=404, detail='players not found')
    return result
