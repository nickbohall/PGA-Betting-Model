from typing import List

import fastapi
from fastapi import Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.db.db_setup import get_db
from app.schemas.player import PlayerBase as PlayerSchema
from app.schemas.common import StatusResponse
from app.crud.players import get_player, get_player_by_name, get_players, update_players, delete_all_players

router = fastapi.APIRouter(
    prefix="/players",
    tags=["players"]
)

db_dependency = Depends(get_db)

@router.get("/", response_model=List[PlayerSchema])
async def get_players_list(db: Session = db_dependency, skip: int = 0, limit: int = 1000):
    """
    Retrieve players with pagination.
    """
    try:
        # Pass skip and limit parameters to get_players
        db_players = get_players(db, skip=skip, limit=limit)
        # Return empty list instead of raising 404
        return db_players
    except HTTPException as he:
        # Re-raise HTTP exceptions with their original status code and detail
        raise he
    except Exception as e:
        # For other exceptions, provide a generic error message
        error_message = str(e)
        if "403" in error_message or "blocked" in error_message.lower():
            # If it's related to access being blocked
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Unable to fetch players: Access to PGA Tour website is blocked. Please try again later."
            )
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching players: {error_message}")

@router.post("/refresh", response_model=StatusResponse, status_code=status.HTTP_202_ACCEPTED)
async def refresh_players_data(background_tasks: BackgroundTasks, db: Session = db_dependency):
    """
    Triggers the addition or update of players as a background task.
    """
    try:
        # Using background tasks for potentially long-running update/scrape
        background_tasks.add_task(update_players, db=db)
        return StatusResponse(status="accepted", message="Player update started in background.")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to start player update: {str(e)}")

@router.delete("/delete-all", response_model=StatusResponse)
async def delete_all_players_endpoint(db: Session = db_dependency):
    """
    Delete all records from the players table.
    This is a destructive operation and cannot be undone.
    """
    try:
        # Call the CRUD function to delete all players
        success, count = delete_all_players(db=db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete players table"
            )
        return StatusResponse(status="success", message=f"Successfully deleted all {count} records from players table")
    except Exception as e:
        # Log the exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete players table: {str(e)}"
        )