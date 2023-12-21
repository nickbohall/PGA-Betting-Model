from sqlalchemy.orm import Session

from app.models.player import Player
from app.services.player_scrape import get_player_info


def get_player(db: Session, player_id: str):
    return db.query(Player).filter(Player.id == player_id).first()

def get_player_by_name(db: Session, player_name: str):
    return db.query(Player).filter(Player.name == player_name).first()

def get_players(db: Session):
    return db.query(Player).all()

def get_player_names(db: Session):
    return db.query(Player.name).all()

def add_players(db: Session):
    player_list = get_player_info()
    for ind_player in player_list:

        db_players = Player(
            id = ind_player["id"], 
            name = ind_player["name"],
            nationality = ind_player["nationality"]
        )

        db.add(db_players)
        db.commit()
    db.refresh(db_players)
    return db_players



