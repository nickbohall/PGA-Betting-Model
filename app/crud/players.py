from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException

from app.models.player import Player
from app.services.player_scrape import get_player_info


def get_player(db: Session, player_id: str):
    return db.query(Player).filter(Player.id == player_id).first()

def get_player_by_name(db: Session, player_name: str):
    return db.query(Player).filter(Player.name == player_name).first()

def get_players(db: Session, skip: int = 0, limit: int = 1000):
    """
    Retrieve players with pagination support.
    
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return (default increased to 1000)
        
    Returns:
        List of Player objects
    """
    return db.query(Player).offset(skip).limit(limit).all()

def get_player_names(db: Session):
    return db.query(Player.name).all()

def create_players(db: Session):
    """
    Create players from scraped data, preventing duplicates.
    
    Args:
        db: Database session
        
    Returns:
        The last created player or an existing player if all were duplicates
    """
    player_list = get_player_info()
    last_player = None
    
    for ind_player in player_list:
        # Check if player already exists
        existing_player = db.query(Player).filter(Player.id == ind_player["id"]).first()
        
        if existing_player:
            # Update player information if changed
            if (existing_player.name != ind_player["name"] or
                    existing_player.nationality != ind_player["nationality"]):
                existing_player.name = ind_player["name"]
                existing_player.nationality = ind_player["nationality"]
                db.commit()
                last_player = existing_player
        else:
            # Add new player
            db_player = Player(
                id = ind_player["id"],
                name = ind_player["name"],
                nationality = ind_player["nationality"]
            )
            
            db.add(db_player)
            db.commit()
            last_player = db_player
    
    return last_player

def update_players(db: Session):
    try:
        player_list = get_player_info()
    except HTTPException as http_exc:
        # Re-raise the exception from get_player_info to be handled by FastAPI
        raise http_exc
    except Exception as e:
        # Catch any other unexpected errors from get_player_info
        print(f"An unexpected error occurred calling get_player_info: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve player info: {e}")

    if not player_list:
        print("No player information retrieved or scraping returned empty list.")
        # Decide how to handle empty list - return empty, raise error?
        # For now, let's return the empty list.
        return []

    try:
        added_count = 0
        updated_count = 0
        for ind_player in player_list:
            # Check if player exists in the database
            existing_player = db.query(Player).filter(Player.id == ind_player["id"]).first()

            if existing_player:
                # Update player information if changed
                if (existing_player.name != ind_player["name"] or
                        existing_player.nationality != ind_player["nationality"]):
                    existing_player.name = ind_player["name"]
                    existing_player.nationality = ind_player["nationality"]
                    updated_count += 1
            else:
                # Add new player
                print(f"\nAdding new player: {ind_player}") # Fixed typo /n -> \n
                db_player = Player(
                    id=ind_player["id"],
                    name=ind_player["name"],
                    nationality=ind_player["nationality"]
                )
                db.add(db_player)
                added_count += 1
        
        if added_count > 0 or updated_count > 0:
            db.commit()
            print(f"Database commit successful. Added: {added_count}, Updated: {updated_count}")
        else:
             print("No new players added or existing players updated.")

        # Optionally, refresh objects if needed after commit, though maybe not necessary here
        # for player in db.new: db.refresh(player)
        # for player in db.dirty: db.refresh(player)

    except SQLAlchemyError as e:
        db.rollback() # Roll back the transaction on error
        print(f"Database error occurred: {e}")
        raise HTTPException(status_code=500, detail=f"Database error during player update: {e}")
    except Exception as e:
        db.rollback() # Roll back on any other unexpected error during DB operations
        print(f"An unexpected error occurred during database operation: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error during player update: {e}")

    return player_list # Return the original scraped list


def delete_all_players(db: Session):
    """
    Delete all records from the players table.
    
    Args:
        db: Database session
        
    Returns:
        Tuple of (success: bool, count: int) where:
        - success: True if operation was successful, False otherwise
        - count: Number of records deleted
    """
    try:
        # Get count of records before deletion
        count = db.query(Player).count()
        
        # Delete all records
        db.query(Player).delete()
        db.commit()
        
        return True, count
    except SQLAlchemyError as e:
        db.rollback()  # Roll back the transaction on error
        print(f"Database error occurred during delete_all_players: {e}")
        return False, 0
    except Exception as e:
        db.rollback()  # Roll back on any other unexpected error
        print(f"An unexpected error occurred during delete_all_players: {e}")
        return False, 0
