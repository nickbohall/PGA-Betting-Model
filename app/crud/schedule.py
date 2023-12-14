from sqlalchemy.orm import Session

from app.models.schedule import Schedule
from app.services.schedule_scrape import get_schedule_info


def get_schedule(db: Session, schedule_id: str):
    return db.query(Schedule).filter(Schedule.id == schedule_id).first()

def get_schedules(db: Session):
    return db.query(Schedule).all()

def add_schedules(db: Session):
    schedule_list = get_schedule_info(db)
    for ind_schedule in schedule_list:

        db_tourneys = Schedule(
            year = ind_schedule['year'],
            tourney_id = ind_schedule['tourney_id'],
            tournament_name = ind_schedule['tourney_name'],
            player_name = ind_schedule['player_name'],
            player_id = ind_schedule['player_id'],
            finish = ind_schedule['finish'],
            score = ind_schedule['score']
        )

        db.add(db_tourneys)
        db.commit()
    db.refresh(db_tourneys)
    return db_tourneys