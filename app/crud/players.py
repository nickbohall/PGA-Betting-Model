from sqlalchemy.orm import Session

from app.models.player import Player


def get_player(db: Session, player_id: str):
    return db.query(Player).filter(Player.id == player_id).first()


def get_player_by_name(db: Session, player_name: str):
    return db.query(Player).filter(Player.name == player_name).first()


def get_players(db: Session, skip: int = 0, limit: int = 300):
    return db.query(Player).offset(skip).limit(limit).all()