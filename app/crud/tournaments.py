from sqlalchemy.orm import Session

from app.models.tournament import Tournament
from app.services.tourney_scrape import get_tourney_info


def get_tournament(db: Session, tournament_id: str):
    return db.query(Tournament).filter(Tournament.id == tournament_id).first()

def get_tournaments(db: Session):
    return db.query(Tournament).all()

def get_tournament_names(db: Session):
    return db.query(Tournament.name).all()

def get_tournament_ids(db: Session):
    return db.query(Tournament.id).all()

def add_tournaments(db: Session):
    tourney_list = get_tourney_info()
    for ind_tourney in tourney_list:

        db_tourneys = Tournament(
            tourney_id = ind_tourney["tournament_id"], 
            tourney_name = ind_tourney["tournament_name"],
            course_name = ind_tourney["course_name"]
        )

        db.add(db_tourneys)
        db.commit()
    db.refresh(db_tourneys)
    return db_tourneys