from typing import List

import fastapi
from fastapi import Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

from app.db.db_setup import get_db
from app.schemas.tournament import Tournament as TournamentSchema
from app.schemas.common import StatusResponse
from app.crud.tournaments import get_tournaments, create_tournaments, delete_all_tournaments

router = fastapi.APIRouter(
    prefix="/tournaments",
    tags=["tournaments"]
)

db_dependency = Depends(get_db)

@router.get("/", response_model=List[TournamentSchema])
async def get_tournaments_list(
    db: Session = db_dependency,
    skip: int = 0,
    limit: int = 1000,
    year: int = None
):
    """
    Retrieve tournaments with pagination and optional year filtering.
    """
    try:
        db_tournaments = get_tournaments(db, skip=skip, limit=limit, year=year)
        # Return empty list instead of raising 404
        return db_tournaments
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
                detail="Unable to fetch tournaments: Access to PGA Tour website is blocked. Please try again later."
            )
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching tournaments: {error_message}")

@router.post("/refresh", response_model=StatusResponse, status_code=status.HTTP_202_ACCEPTED)
async def refresh_tournaments_data(background_tasks: BackgroundTasks, db: Session = db_dependency):
    """
    Triggers the addition or update of tournaments as a background task.
    """
    try:
        # Using background tasks for potentially long-running update/scrape
        background_tasks.add_task(create_tournaments, db=db)
        return StatusResponse(status="accepted", message="Tournament update started in background.")
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
                detail="Unable to refresh tournaments: Access to PGA Tour website is blocked. Please try again later."
            )
        else:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to start tournament update: {error_message}")

@router.delete("/delete-all", response_model=StatusResponse)
async def delete_all_tournaments_endpoint(db: Session = db_dependency):
    """
    Delete all records from the tournaments table.
    This is a destructive operation and cannot be undone.
    """
    try:
        # Call the CRUD function to delete all tournaments
        success, count = delete_all_tournaments(db=db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete tournaments table"
            )
        return StatusResponse(status="success", message=f"Successfully deleted all {count} records from tournaments table")
    except Exception as e:
        # Log the exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete tournaments table: {str(e)}"
        )