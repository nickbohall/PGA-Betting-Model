from typing import List

import fastapi
from fastapi import Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.db.db_setup import get_db
from app.schemas.player_stats import PlayerStat as PlayerStatSchema
from app.schemas.common import StatusResponse
from app.crud.player_stats import update_player_stats, get_player_stats, delete_all_player_stats


router = fastapi.APIRouter(
    prefix="/player-stats", # Changed to kebab-case for URL convention
    tags=["player_stats"]   # Kept tag as is for UI organization
)

db_dependency = Depends(get_db)

# GET /player_stats - Get list of player stats with pagination
@router.get("/", response_model=List[PlayerStatSchema])
async def get_player_statistics(db: Session = db_dependency, skip: int = 0, limit: int = 1000):
    """
    Retrieve player statistics with pagination.
    Assumes get_player_stats in crud supports skip/limit.
    """
    try:
        # Assumes get_player_stats is updated to accept skip/limit
        db_player_stats = get_player_stats(db=db, skip=skip, limit=limit)
    except Exception as e:
        # Catch potential DB errors or issues in the CRUD function
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching player stats: {e}")

    # Note: Depending on CRUD logic, it might return empty list instead of raising error
    # if not db_player_stats:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No player stats found")
    return db_player_stats

# POST /player_stats/refresh - Trigger update/add player stats
@router.post("/refresh", response_model=StatusResponse, status_code=status.HTTP_202_ACCEPTED)
async def refresh_player_statistics(background_tasks: BackgroundTasks, db: Session = db_dependency):
    """
    Triggers the addition or update of player statistics as a background task.
    Currently assumes it updates/adds all relevant stats without specific input.
    Consider adding parameters if specific players/timeframes are needed.
    Assumes add_or_update_player_stats handles the core logic.
    """
    try:
        # Using background tasks for potentially long-running update/scrape
        # Assumes add_or_update_player_stats can run independently or is adapted for background tasks
        # Note: Passing the db session directly to background task might be problematic
        # depending on session scope. Consider passing necessary IDs or using dependency injection.
        background_tasks.add_task(update_player_stats, db=db)
        return StatusResponse(status="accepted", message="Player stats update started in background.")
    except Exception as e:
        # Log the exception e
        # Error likely occurs if task cannot be added or initial setup fails
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to start player stats update: {e}")

@router.delete("/delete-all", response_model=StatusResponse)
async def delete_all_player_stats_endpoint(db: Session = db_dependency):
    """
    Delete all records from the player_stats table.
    This is a destructive operation and cannot be undone.
    """
    try:
        # Call the CRUD function to delete all player stats
        success, count = delete_all_player_stats(db=db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete player stats table"
            )
        return StatusResponse(status="success", message=f"Successfully deleted all {count} records from player stats table")
    except Exception as e:
        # Log the exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete player stats table: {str(e)}"
        )

# Removed commented out code block
