from typing import List

import fastapi
from fastapi import Depends, HTTPException, BackgroundTasks, status
from sqlalchemy.orm import Session

# Local Imports
from app.db.db_setup import get_db
from app.schemas.master import Master as MasterSchema
from app.schemas.common import StatusResponse
from app.crud.master import (
    get_masters_table,
    create_tournament_record,
    update_sg_stats,
    import_historical_data,
    update_tournament_results,
    run_master_scrape,
    delete_table,
    delete_all_master,
    add_player_stats_for_tournament
)

router = fastapi.APIRouter(
    prefix="/master", # Changed to singular for consistency
    tags=["master"]   # Changed to singular for consistency
)

db_dependency = Depends(get_db)

# GET /masters - Get list of master records with pagination
@router.get("/", response_model=List[MasterSchema])
async def get_master_records(db: Session = db_dependency, skip: int = 0, limit: int = 10000):
    """
    Retrieve master tournament records with pagination.
    Assumes get_masters_table in crud supports skip/limit.
    """
    try:
        # Assumes get_masters_table is updated to accept skip/limit
        db_masters = get_masters_table(db=db, skip=skip, limit=limit)
    except Exception as e:
        # Catch potential DB errors or issues in the CRUD function
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error fetching masters: {e}")

    # Note: Depending on CRUD logic, it might return empty list instead of raising error
    # if not db_masters:
    #     raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No masters found")
    return db_masters

# POST /masters/tournaments/{tournament_name} - Add a new tournament entry
@router.post("/tournaments/{tournament_name}", response_model=MasterSchema, status_code=status.HTTP_201_CREATED)
async def create_tournament_record_endpoint(tournament_name: str, year: int, db: Session = db_dependency):
    """
    Add a new tournament entry to the master table.
    
    Parameters:
    - tournament_name: Name of the tournament
    - year: Year of the tournament
    """
    try:
        created_master = create_tournament_record(tournament_name=tournament_name, year=year, db=db)
        if created_master is None:
             raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not create master entry, check input data.")
        return created_master
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to create master entry: {str(e)}")

# PATCH /masters/{tournament_name}/{year}/sg_stats - Update SG stats
@router.patch("/{tournament_name}/{year}/sg_stats", response_model=StatusResponse)
async def update_sg_statistics(tournament_name: str, year: int, db: Session = db_dependency):
    """
    Update Strokes Gained (SG) statistics for a specific tournament and year.
    Assumes update_sg_stats returns success/failure or raises Exception.
    """
    try:
        # Assumes update_sg_stats is updated to return status or raise error
        success = update_sg_stats(tournament_name=tournament_name, year=year, db=db)
        if not success: # Or check specific return value indicating failure
             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tournament {tournament_name} ({year}) not found or update failed.")
        return StatusResponse(status="success", message=f"SG stats updated for {tournament_name} ({year}).")
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update SG stats: {e}")

# POST /masters/import/historical - Trigger historical data import
@router.post("/import/historical", response_model=StatusResponse, status_code=status.HTTP_202_ACCEPTED)
async def import_historical_data(background_tasks: BackgroundTasks, db: Session = db_dependency):
    """
    Triggers the import of historical data from a CSV file as a background task.
    Assumes get_historical_data_from_csv handles the import logic.
    """
    try:
        # Using background tasks for potentially long-running import
        # Assumes get_historical_data_from_csv can run independently or is adapted for background tasks
        background_tasks.add_task(import_historical_data, db=db)
        return StatusResponse(status="accepted", message="Historical data import started in background.")
    except Exception as e:
        # Log the exception e
        # Error likely occurs if task cannot be added or initial setup fails
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to start historical data import: {e}")

# PATCH /masters/{tournament_name}/{year}/finishes - Add/Update tournament finishes
@router.patch("/{tournament_name}/{year}/finishes", response_model=StatusResponse)
async def update_tournament_results(tournament_name: str, year: int, db: Session = db_dependency):
    """
    Add or update tournament finish data for a specific tournament and year.
    Assumes add_tourney_finishes_to_master returns success/failure or raises Exception.
    """
    try:
        # Assumes add_tourney_finishes_to_master is updated to return status or raise error
        success = update_tournament_results(tournament_name=tournament_name, year=year, db=db)
        if not success: # Or check specific return value indicating failure
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Tournament {tournament_name} ({year}) not found or update failed.")
        return StatusResponse(status="success", message=f"Tournament finishes updated for {tournament_name} ({year}).")
    except Exception as e:
        # Log the exception e
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to update tournament finishes: {e}")
# Removed the /test endpoint

# POST /master/refresh - Trigger full master data refresh
@router.post("/refresh", response_model=StatusResponse, status_code=status.HTTP_202_ACCEPTED)
async def refresh_master_data(background_tasks: BackgroundTasks, db: Session = db_dependency):
    """
    Triggers a full refresh of the master data table by scraping all tournament results.
    This is a potentially long-running operation that runs in the background.
    """
    try:
        # Run the master scrape process in the background
        background_tasks.add_task(run_master_scrape, db=db)
        return StatusResponse(status="accepted", message="Master data refresh started in background. This may take a while.")
    except Exception as e:
        # Log the exception
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to start master data refresh: {e}")

# DELETE /master/{tournament_name}/{year} - Delete a tournament table
@router.delete("/{tournament_name}/{year}", response_model=StatusResponse)
async def delete_tournament_table(tournament_name: str, year: int, db: Session = db_dependency):
    """
    Delete all records for a specific tournament and year from the master table.
    
    Parameters:
    - tournament_name: Name of the tournament to delete
    - year: Year of the tournament to delete
    """
    try:
        success = delete_table(tournament_name=tournament_name, year=year, db=db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tournament {tournament_name} ({year}) not found or delete failed."
            )
        return StatusResponse(status="success", message=f"Tournament {tournament_name} ({year}) deleted successfully.")
    except Exception as e:
        # Log the exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete tournament: {e}"
        )

# POST /master/{tournament_name}/{year}/player-stats - Add player stats for a tournament
@router.post("/{tournament_name}/{year}/player-stats", response_model=StatusResponse)
async def add_player_stats_for_tournament_endpoint(tournament_name: str, year: int, db: Session = db_dependency):
    """
    Add player stats for a specific tournament and year to the master table.
    This copies the player stats from the player_stats table to the master table
    for all players participating in the specified tournament.
    
    Parameters:
    - tournament_name: Name of the tournament
    - year: Year of the tournament
    """
    try:
        success = add_player_stats_for_tournament(tournament_name=tournament_name, year=year, db=db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Tournament {tournament_name} ({year}) not found or no player stats available."
            )
        return StatusResponse(status="success", message=f"Player stats added for {tournament_name} ({year}).")
    except Exception as e:
        # Log the exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add player stats: {e}"
        )

@router.delete("/delete-all", response_model=StatusResponse)
async def delete_all_master_endpoint(db: Session = db_dependency):
    """
    Delete all records from the master table.
    This is a destructive operation and cannot be undone.
    """
    try:
        # Call the CRUD function to delete all master records
        success, count = delete_all_master(db=db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete master table"
            )
        return StatusResponse(status="success", message=f"Successfully deleted all {count} records from master table")
    except Exception as e:
        # Log the exception
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete master table: {e}"
        )