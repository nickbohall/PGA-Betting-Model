# Package Imports
from fastapi import FastAPI

from app.api import players, player_stats, schedule, tournaments
from app.db.db_setup import engine
from app.models import player as playermodel, player_stats as player_statsmodel, schedule as schedulemodel, tournament as tournamentmodel


playermodel.Base.metadata.create_all(bind=engine)
player_statsmodel.Base.metadata.create_all(bind=engine)
schedulemodel.Base.metadata.create_all(bind=engine)
tournamentmodel.Base.metadata.create_all(bind=engine)


app = FastAPI()

app.include_router(players.router)
app.include_router(player_stats.router)
app.include_router(schedule.router)
app.include_router(tournaments.router)

@app.get("/")
async def root():
    return {"message": "This is a PGA Betting Model"}
    

