# Package Imports
import logging
import os
import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from app.api import master, players, player_stats, tournaments
from app.db.db_setup import engine
from app.models import master as masteremodel, player as playermodel, player_stats as player_statsmodel, tournament as tournamentmodel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("pga_betting_model")


playermodel.Base.metadata.create_all(bind=engine)
player_statsmodel.Base.metadata.create_all(bind=engine)
masteremodel.Base.metadata.create_all(bind=engine)
tournamentmodel.Base.metadata.create_all(bind=engine)
app = FastAPI(
    title="PGA Betting Model API",
    description="API for PGA Tour betting model data",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development - restrict this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add middleware for request timing and logging
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        logger.info(f"Request to {request.url.path} completed in {process_time:.2f}s")
        return response
    except Exception as e:
        logger.error(f"Error processing request to {request.url.path}: {str(e)}")
        process_time = time.time() - start_time
        return JSONResponse(
            status_code=500,
            content={"detail": f"Internal server error: {str(e)}"}
        )

app.include_router(players.router)
app.include_router(player_stats.router)
app.include_router(master.router)
app.include_router(tournaments.router)

# Mount static files
import os
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
async def root():
    # Redirect to the static frontend
    from fastapi.responses import FileResponse
    return FileResponse(os.path.join(static_dir, "index.html"))
