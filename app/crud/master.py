from sqlalchemy.orm import Session
from sqlalchemy import update

from app.models.master import Master
from app.models.player_stats import PlayerStat
from app.models.tournament import Tournament
from app.models.player import Player

from app.services.master_scrape import get_current_tourney
from app.services.pga_data_import import get_historical_data
from app.crud.player_stats import get_player_stats_for_tourney


def get_master_by_tourney(db: Session, master_id: str):
    return db.query(Master).filter(Master.id == master_id).first()

def get_masters_table(db: Session):
    return db.query(Master).all()

def add_new_tourney_to_master(tournament_name, db: Session):
    master_list = get_current_tourney(db=db, tourney_name=tournament_name)

    
    for row in master_list:

        player_id = db.query(Player.id).filter(Player.name == row['player_name']).scalar()
        course_name = db.query(Tournament).filter(Tournament.tourney_name == row['tourney_name']).first().course_name

        new_tourney = Master(
            year = row['year'],
            tourney_id = row['tourney_id'],
            tournament_name = row['tourney_name'],
            course_name= course_name or "NAN",
            player_name = row['player_name'],
            player_id = player_id or "NAN",
            odds = row['odds']
        )

        db.add(new_tourney)
        db.commit()

    return None


def update_sg_stats(tournament_name: str, year: int, db: Session) -> None:
    # Get player names from Master table
    player_ids = [player.player_id for player in db.query(Master)
                    .filter_by(tournament_name=tournament_name, year=year)]

    # Get player stats using bulk_load for efficiency
    player_stats = {player.id: player for player in
                    db.query(PlayerStat).filter(PlayerStat.id.in_(player_ids)).all()}

    # Update Master table with statistics
    for player_id, stats in player_stats.items():

        update_dict = {
            'sg_total': getattr(stats, 'sg_apr'),
            'sg_ttg': getattr(stats, 'sg_atg'),
            'sg_ott': getattr(stats, 'sg_ott'),
            'sg_apr': getattr(stats, 'sg_putt'),
            'sg_atg': getattr(stats, 'sg_total'),
            'sg_putt': getattr(stats, 'sg_ttg'),
        }

        db.query(Master) \
            .filter_by(player_id=player_id,
                    tournament_name=tournament_name,
                    year=year) \
            .update(update_dict)

    db.commit()  # Commit changes to the database
    return None  # This function doesn't return data, so return None

def get_historical_data_from_csv(db: Session):
    data_for_sql = get_historical_data()

    for row in data_for_sql:
        # Retrieve the Tournament object from the database
        tournament = db.query(Tournament).filter(Tournament.tourney_name == row['tournament_name']).first()

        # If the tournament is not found, set tourney_id to "NAN"
        tourney_id = tournament.tourney_id if tournament else "NAN"

        player_id = db.query(Player.id).filter(Player.name == row['player_name']).scalar()

        db_tourneys = Master(
            year=row['year'],
            tourney_id=tourney_id,  # Use "NAN" if tourney_id is None
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