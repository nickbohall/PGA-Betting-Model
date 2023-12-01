from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Annotated
from sqlalchemy.orm import Session

from .models import Player, Tournament, Schedule
from .schema import Player as SchemaPlayer, Tournament as SchemaTournament, Schedule as SchemaSchedule
from .database import engine, SessionLocal
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
    player = Player(id=player.player_id, name=player.player_name, nationality=player.player_nationality)
    db.add(player)
    db.commit()
    db.refresh(db)

@app.get("/players")
def get_players():
    result = db.query(Player).all()
    if not result:
        raise HTTPException(status_code=404, detail='players not found')
    return result







# players = PgaScrape()
# player_info = players.get_player_info()
