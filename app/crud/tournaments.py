from sqlalchemy.orm import Session

from app.models.tournament import Tournament
from app.services.tourney_scrape import get_tournament_data


def get_tournament(db: Session, tournament_id: str, year: int = None):
    query = db.query(Tournament).filter(Tournament.tournament_id == tournament_id)
    if year:
        query = query.filter(Tournament.year == year)
    return query.first()

def get_tournaments(db: Session, skip: int = 0, limit: int = 1000, year: int = None):
    """
    Retrieve tournaments with pagination support and optional year filtering.
    
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        year: Optional year to filter tournaments by
        
    Returns:
        List of Tournament objects
    """
    query = db.query(Tournament)
    
    if year:
        query = query.filter(Tournament.year == year)
        
    return query.offset(skip).limit(limit).all()

def get_tournament_names(db: Session):
    return db.query(Tournament.tournament_name).all()

def get_tournament_ids(db: Session):
    return db.query(Tournament.tournament_id).all()

def create_tournaments(db: Session):
    """
    Create tournaments from scraped data, preventing duplicates.
    
    Args:
        db: Database session
        
    Returns:
        The last created tournament or an existing tournament if all were duplicates
    """
    tourney_list = get_tournament_data()
    last_tournament = None
    
    for ind_tourney in tourney_list:
        # Check if tournament already exists for this year
        existing_tournament = db.query(Tournament).filter(
            Tournament.tournament_name == ind_tourney["tournament_name"],
            Tournament.year == ind_tourney["year"]
        ).first()
        
        if existing_tournament:
            # Update tournament information if changed
            if (existing_tournament.tournament_id != ind_tourney["tournament_id"] or
                    existing_tournament.course_name != ind_tourney["course_name"] or
                    existing_tournament.tournament_date != ind_tourney.get("tournament_date")):
                existing_tournament.tournament_id = ind_tourney["tournament_id"]
                existing_tournament.course_name = ind_tourney["course_name"]
                existing_tournament.tournament_date = ind_tourney.get("tournament_date")
                db.commit()
                last_tournament = existing_tournament
        else:
            # Add new tournament
            db_tournament = Tournament(
                tournament_id = ind_tourney["tournament_id"],
                tournament_name = ind_tourney["tournament_name"],
                course_name = ind_tourney["course_name"],
                year = ind_tourney["year"],
                tournament_date = ind_tourney.get("tournament_date")
            )
            
            db.add(db_tournament)
            db.commit()
            last_tournament = db_tournament
    
    return last_tournament

def delete_all_tournaments(db: Session):
    """
    Delete all records from the tournaments table.
    
    Args:
        db: Database session
        
    Returns:
        Tuple of (success: bool, count: int) where:
        - success: True if operation was successful, False otherwise
        - count: Number of records deleted
    """
    try:
        # Get count of records before deletion
        count = db.query(Tournament).count()
        
        # Delete all records
        db.query(Tournament).delete()
        db.commit()
        
        return True, count
    except Exception as e:
        db.rollback()  # Roll back the transaction on error
        print(f"Error deleting tournaments: {e}")
        return False, 0