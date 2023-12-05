from sqlalchemy.orm import Session

from app.models.player import Player
from app.services.player_scrape import get_player_info


def get_player(db: Session, player_id: str):
    return db.query(Player).filter(Player.id == player_id).first()

def get_player_by_name(db: Session, player_name: str):
    return db.query(Player).filter(Player.name == player_name).first()

def get_players(db: Session, skip: int = 0, limit: int = 300):
    return db.query(Player).offset(skip).limit(limit).all()

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

from app.services.player_stats_scrape import get_player_stats

