from sqlalchemy.orm import Session
from sqlalchemy import update

from app.models.master import Master
from app.models.player_stats import PlayerStat
from app.models.tournament import Tournament
from app.models.player import Player

from app.services.master_scrape import get_master_info
from app.services.pga_data_import import get_historical_data
from app.crud.player_stats import get_player_stats_for_tourney


def get_master_by_tourney(db: Session, master_id: str):
    return db.query(Master).filter(Master.id == master_id).first()

def get_masters_table(db: Session):
    return db.query(Master).all()

def add_master_table(db: Session):
    master_list = get_master_info(db)
    for ind_master in master_list:

        db_tourneys = Master(
            year = ind_master['year'],
            tourney_id = ind_master['tourney_id'],
            tournament_name = ind_master['tourney_name'],
            course_name= ind_master['course_name'],
            player_name = ind_master['player_name'],
            player_id = ind_master['player_id'],
            finish = ind_master['finish'],
            score = ind_master['score']
        )

        db.add(db_tourneys)
        db.commit()
    db.refresh(db_tourneys)
    return db_tourneys


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
        tournament = db.query(Tournament).filter(Tournament.name == row['tournament_name']).first()

        # If the tournament is not found, set tourney_id to "NAN"
        tourney_id = tournament.id if tournament else "NAN"

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