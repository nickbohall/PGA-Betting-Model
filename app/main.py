# Package Imports
from fastapi import FastAPI

from app.api import players, schedule, tournaments
from app.db.db_setup import engine
from app.models import player, schedule, tournament

player.Base.metadata.create_all(bind=engine)
schedule.Base.metadata.create_all(bind=engine)
tournament.Base.metadata.create_all(bind=engine)

app = FastAPI(separate_input_output_schemas=False)

app.include_router(players.router)
# app.include_router(schedule.router)
# app.include_router(tournaments.router)

@app.get("/")
async def root():
    return {"message": "This is a PGA Betting Model"}

