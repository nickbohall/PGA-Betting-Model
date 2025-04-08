from sqlalchemy.orm import Session
from sqlalchemy import update, delete
from pydantic import ValidationError
from sqlalchemy.future import select

from app.models.master import Master
from app.models.player_stats import PlayerStat
from app.models.tournament import Tournament
from app.models.player import Player

from app.services.master_scrape import scrape_master_data, get_tournament_results
from app.services.pga_data_import import get_historical_data
from app.services.finish_scrape import get_tournament_results as get_finish_results
from app.crud.player_stats import get_player_stats_by_tournament


def get_master_by_id(db: Session, master_id: str):
    return db.query(Master).filter(Master.id == master_id).first()

def get_masters_table(db: Session, skip: int = 0, limit: int = 10000):
    """
    Retrieve master records with pagination support.
    
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        
    Returns:
        List of Master objects
    """
    query = select(Master).offset(skip).limit(limit)
    result = db.execute(query)
    return result.scalars().fetchall()

def create_tournament_record(tournament_name, year, db: Session):
    """
    Create tournament records for a specific tournament and year.
    Uses the scrape_single_tournament service to get players for the tournament.
    
    Parameters:
    - tournament_name: Name of the tournament
    - year: Year of the tournament
    - db: Database session
    
    Returns:
    - The last created tournament record or an existing record if found
    """
    import logging
    from app.services.master_scrape import scrape_single_tournament
    
    logger = logging.getLogger("pga_betting_model.master_crud")
    
    # Check if tournament + year combination already exists
    existing_records = db.query(Master).filter(
        Master.tournament_name == tournament_name,
        Master.year == year
    ).first()
    
    if existing_records:
        # Return the existing record instead of creating duplicates
        logger.info(f"Tournament {tournament_name} ({year}) already exists in master table")
        return existing_records
    
    # Use the scrape_single_tournament service to get players for this tournament
    result = scrape_single_tournament(tournament_name, year, db)
    
    if result["status"] != "success":
        logger.error(f"Failed to add tournament {tournament_name} ({year}): {result['message']}")
        return None
    
    # Return the first record for this tournament and year
    last_record = db.query(Master).filter(
        Master.tournament_name == tournament_name,
        Master.year == year
    ).first()
    
    return last_record

def update_sg_stats(tournament_name: str, year: int, db: Session) -> bool:
    """
    Update Strokes Gained statistics for a specific tournament and year.
    
    Parameters:
    - tournament_name: Name of the tournament
    - year: Year of the tournament
    - db: Database session
    
    Returns:
    - True if successful, False if no records found
    """
    # Get player records from Master table for this specific tournament and year
    master_records = db.query(Master).filter_by(
        tournament_name=tournament_name,
        year=year
    ).all()
    
    if not master_records:
        return False  # No records found for this tournament + year
    
    player_ids = [record.player_id for record in master_records]

    # Get player stats using bulk_load for efficiency
    player_stats = {player.id: player for player in
                   db.query(PlayerStat).filter(PlayerStat.id.in_(player_ids)).all()}

    # Update Master table with statistics
    for record in master_records:
        if record.player_id in player_stats:
            stats = player_stats[record.player_id]
            
            update_dict = {
                'sg_total': getattr(stats, 'sg_total'),
                'sg_ttg': getattr(stats, 'sg_atg'),
                'sg_ott': getattr(stats, 'sg_ott'),
                'sg_apr': getattr(stats, 'sg_apr'),
                'sg_atg': getattr(stats, 'sg_atg'),
                'sg_putt': getattr(stats, 'sg_putt'),
            }

            # Update this specific record
            db.query(Master) \
                .filter_by(id=record.id) \
                .update(update_dict)

    db.commit()  # Commit changes to the database
    return True  # Successfully updated

def import_historical_data(db: Session):
    data_for_sql = get_historical_data()

    for row in data_for_sql:
        # Retrieve the Tournament object from the database
        tournament = db.query(Tournament).filter(Tournament.tournament_name == row['tournament_name']).first()

        # If the tournament is not found, set tourney_id to "NAN"
        tourney_id = tournament.tournament_id if tournament else "NAN"

        player_id = db.query(Player.id).filter(Player.name == row['player_name']).scalar()

        db_tourneys = Master(
            year=row['year'],
            tournament_id=tourney_id,  # Use "NAN" if tournament_id is None
            tournament_name=row['tournament_name'],
            course_name=row['course_name'],
            player_name=row['player_name'],
            player_id=player_id or 99999,  # Use "NAN" if player_id is None
            finish=row['finish'],
            score=row['score'],
            sg_total=row['weighted_sg_total'],
            sg_ttg=row['weighted_sg_t2g'],
            sg_ott=row['weighted_sg_ott'],
            sg_apr=row['weighted_sg_app'],
            sg_atg=row['weighted_sg_arg'],
            sg_putt=row['weighted_sg_putt']
        )

        db.add(db_tourneys)
        db.commit()
    db.refresh(db_tourneys)
    print("Historical data added to db!")
    return db_tourneys

def update_tournament_results(tournament_name, year, db: Session):
    """
    Update tournament results for a specific tournament and year.
    
    Parameters:
    - tournament_name: Name of the tournament
    - year: Year of the tournament
    - db: Database session
    
    Returns:
    - True if successful, False if no records found
    """
    # Check if tournament + year combination exists
    existing_records = db.query(Master).filter(
        Master.tournament_name == tournament_name,
        Master.year == year
    ).first()
    
    if not existing_records:
        return False  # No records found for this tournament + year
    
    # Get tournament ID from the database
    tournament = db.query(Tournament).filter(Tournament.tournament_name == tournament_name).first()
    if not tournament:
        return False  # Tournament not found
    
    # Use the service function to get tournament results
    from app.services.master_scrape import scrape_tournament_results
    
    player_finishes = scrape_tournament_results(
        tournament_name=tournament_name,
        tournament_id=tournament.tournament_id,
        year=year,
        course_name=tournament.course_name
    )
    
    if not player_finishes:
        return False  # No results found

    # Update Master table with statistics
    for row in player_finishes:
        player = db.query(Player).filter(Player.name == row['player_name']).first()

        # If the player is not found, set player_id to "NAN"
        player_id = player.id if player else "NAN"
        
        update_dict = {
            "finish": row['finish'],
            "score": row['score'],
        }

        # Update only the specific record for this player in this tournament + year
        db.query(Master) \
        .filter_by(
            player_id=player_id,
            tournament_name=tournament_name,
            year=year
        ) \
        .update(update_dict)

    db.commit()  # Commit changes to the database
    return True  # Successfully updated
def run_master_scrape(db: Session):
    """
    Run the master scrape process to get all tournament results.
    
    Parameters:
    - db: Database session
    
    Returns:
    - Result dictionary with status and message
    """
    return scrape_master_data()

def delete_table(db: Session, tournament_name: str, year: int) -> bool:
    """
    Delete all records for a specific tournament and year from the master table.
    
    Parameters:
    - db: Database session
    - tournament_name: Name of the tournament to delete
    - year: Year of the tournament to delete
    
    Returns:
    - True if successful, False if no records found
    """
    # Check if tournament + year combination exists
    existing_records = db.query(Master).filter(
        Master.tournament_name == tournament_name,
        Master.year == year
    ).first()
    
    if not existing_records:
        return False  # No records found for this tournament + year
    
    # Delete all records for this tournament and year
    stmt = delete(Master).where(
        Master.tournament_name == tournament_name,
        Master.year == year
    )
    
    result = db.execute(stmt)
    db.commit()
    
    return result.rowcount > 0  # Return True if at least one row was deleted

def delete_all_master(db: Session):
    """
    Delete all records from the master table.
    
    Parameters:
    - db: Database session
    
    Returns:
    - Tuple of (success: bool, count: int) where:
      - success: True if operation was successful, False otherwise
      - count: Number of records deleted
    """
    try:
        # Get count of records before deletion
        count = db.query(Master).count()
        
        # Delete all records
        db.query(Master).delete()
        db.commit()
        
        return True, count
    except Exception as e:
        db.rollback()  # Roll back the transaction on error
        print(f"Error deleting master table: {e}")
        return False, 0

def add_player_stats_for_tournament(tournament_name: str, year: int, db: Session) -> bool:
    """
    Add player stats for a specific tournament and year to the master table.
    This function copies player stats from the player_stats table to the master table
    for all players participating in the specified tournament.
    
    Parameters:
    - tournament_name: Name of the tournament
    - year: Year of the tournament
    - db: Database session
    
    Returns:
    - True if successful, False if no records found
    """
    # Check if tournament + year combination exists
    existing_records = db.query(Master).filter(
        Master.tournament_name == tournament_name,
        Master.year == year
    ).all()
    
    if not existing_records:
        return False  # No records found for this tournament + year
    
    # Get all player IDs from the master table for this tournament and year
    player_ids = [record.player_id for record in existing_records]
    
    # Get player stats for these players
    player_stats = {player.id: player for player in
                   db.query(PlayerStat).filter(PlayerStat.id.in_(player_ids)).all()}
    
    # Update Master table with statistics
    updated_count = 0
    for record in existing_records:
        if record.player_id in player_stats:
            stats = player_stats[record.player_id]
            
            update_dict = {
                'sg_total': getattr(stats, 'sg_total'),
                'sg_ttg': getattr(stats, 'sg_ttg'),
                'sg_ott': getattr(stats, 'sg_ott'),
                'sg_apr': getattr(stats, 'sg_apr'),
                'sg_atg': getattr(stats, 'sg_atg'),
                'sg_putt': getattr(stats, 'sg_putt'),
            }
            
            # Update this specific record
            db.query(Master) \
                .filter_by(id=record.id) \
                .update(update_dict)
            
            updated_count += 1
    
    db.commit()  # Commit changes to the database
    print(f"Updated player stats for {updated_count} players in {tournament_name} ({year})")
    return updated_count > 0  # Return True if at least one record was updated