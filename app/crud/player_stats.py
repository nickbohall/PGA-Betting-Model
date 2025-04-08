from sqlalchemy.orm import Session

from app.models.player_stats import PlayerStat
from app.models.master import Master
from app.models.player import Player

from app.services.player_stats_scrape import scrape_player_stats


def get_player_stats(db: Session, skip: int = 0, limit: int = 1000):
    """
    Retrieve player statistics with pagination support.
    
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
        
    Returns:
        List of PlayerStat objects
    """
    return db.query(PlayerStat).offset(skip).limit(limit).all()

def get_player_stats_by_tournament(db:Session, tournament_name):
    return db.query(PlayerStat).filter(Master.tournament_name == tournament_name)

def update_player_stats(db: Session):
    """
    Update player statistics from scraped data, preventing duplicates.
    
    Args:
        db: Database session
        
    Returns:
        List of player statistics
    """
    player_stats = scrape_player_stats(db)

    updated_players = []
    added_players = []

    try:
        for player_stat in player_stats:
            # Check if player exists in the database
            existing_player = db.query(PlayerStat).filter(PlayerStat.name == player_stat["player_name"]).first()
            
            # Check if all stats are None or default values (0.0) - if so, skip this player
            all_default = all(
                player_stat.get(stat) is None or player_stat.get(stat, 0.0) == 0.0
                for stat in ["SG: Total", "SG: T2G", "SG: OTT", "SG: APR", "SG: ATG", "SG: PUTT"]
            )
            
            if all_default:
                print(f"Skipping player {player_stat['player_name']} - no stats found")
                continue

            if existing_player:
                # Update player statistics using get() for safer dictionary access
                # Only update if the value is not None and not the default 0.0
                sg_total = player_stat.get("SG: Total")
                if sg_total is not None and (sg_total != 0.0 or existing_player.sg_total is None):
                    existing_player.sg_total = sg_total
                
                sg_ttg = player_stat.get("SG: T2G")
                if sg_ttg is not None and (sg_ttg != 0.0 or existing_player.sg_ttg is None):
                    existing_player.sg_ttg = sg_ttg
                
                sg_ott = player_stat.get("SG: OTT")
                if sg_ott is not None and (sg_ott != 0.0 or existing_player.sg_ott is None):
                    existing_player.sg_ott = sg_ott
                
                sg_apr = player_stat.get("SG: APR")
                if sg_apr is not None and (sg_apr != 0.0 or existing_player.sg_apr is None):
                    existing_player.sg_apr = sg_apr
                
                sg_atg = player_stat.get("SG: ATG")
                if sg_atg is not None and (sg_atg != 0.0 or existing_player.sg_atg is None):
                    existing_player.sg_atg = sg_atg
                
                sg_putt = player_stat.get("SG: PUTT")
                if sg_putt is not None and (sg_putt != 0.0 or existing_player.sg_putt is None):
                    existing_player.sg_putt = sg_putt

                updated_players.append(existing_player)
            else:
                try:
                    # Check if all stats are None or default values (0.0) - if so, skip this player
                    all_default = all(
                        player_stat.get(stat) is None or player_stat.get(stat, 0.0) == 0.0
                        for stat in ["SG: Total", "SG: T2G", "SG: OTT", "SG: APR", "SG: ATG", "SG: PUTT"]
                    )
                    
                    if all_default:
                        print(f"Skipping new player {player_stat['player_name']} - no stats found")
                        continue
                    
                    # Use player_id directly from the stats if available
                    player_id = player_stat.get("player_id")
                    
                    # If player_id is not in the stats, try to look it up
                    if not player_id:
                        player = db.query(Player).filter(Player.name == player_stat["player_name"]).first()
                        if player:
                            player_id = player.id
                        else:
                            # Player not found in database, create a new player entry
                            print(f"Player not found in database: {player_stat['player_name']}. Creating new player entry.")
                            
                            # Generate a temporary ID for the player (using name as a base)
                            import hashlib
                            # Create a hash of the player name to use as ID
                            player_id = hashlib.md5(player_stat["player_name"].encode()).hexdigest()[:10]
                            
                            # Create new player
                            new_player = Player(
                                id=player_id,
                                name=player_stat["player_name"],
                                nationality="Unknown"  # Default nationality since we don't have this info
                            )
                            
                            try:
                                db.add(new_player)
                                db.flush()  # Flush to get the ID without committing
                                print(f"Created new player: {player_stat['player_name']} with ID: {player_id}")
                            except Exception as e:
                                print(f"Error creating new player {player_stat['player_name']}: {e}")
                                continue
                    
                    # Add new player statistics - allow None values
                    db_player_stats = PlayerStat(
                        name=player_stat["player_name"],
                        id=player_id,
                        sg_total=player_stat.get("SG: Total"),
                        sg_ttg=player_stat.get("SG: T2G"),
                        sg_ott=player_stat.get("SG: OTT"),
                        sg_apr=player_stat.get("SG: APR"),
                        sg_atg=player_stat.get("SG: ATG"),
                        sg_putt=player_stat.get("SG: PUTT"),
                    )
                    db.add(db_player_stats)
                    added_players.append(db_player_stats)
                except KeyError as e:
                    print(f"Missing key for {player_stat['player_name']}: {e}")
                except Exception as e:
                    print(f"Error processing stats for {player_stat['player_name']}: {e}")
        
        # Commit all changes at once
        db.commit()
        print(f"DB Updated! Updated {len(updated_players)} players, added {len(added_players)} players.")
    except Exception as e:
        db.rollback()
        print(f"Error updating player stats: {e}")
        import traceback
        traceback.print_exc()
        raise
        
    return player_stats

def delete_all_player_stats(db: Session):
    """
    Delete all records from the player_stats table.
    
    Args:
        db: Database session
        
    Returns:
        Tuple of (success: bool, count: int) where:
        - success: True if operation was successful, False otherwise
        - count: Number of records deleted
    """
    try:
        # Get count of records before deletion
        count = db.query(PlayerStat).count()
        
        # Delete all records
        db.query(PlayerStat).delete()
        db.commit()
        
        return True, count
    except Exception as e:
        db.rollback()  # Roll back the transaction on error
        print(f"Error deleting player stats: {e}")
        import traceback
        traceback.print_exc()
        return False, 0
