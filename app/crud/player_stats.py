from sqlalchemy.orm import Session

from app.models.player_stats import PlayerStat

from app.services.player_stats_scrape import scrape_player_stats


def get_player_stats(db: Session, skip: int = 0, limit: int = 300):
    return db.query(PlayerStat).all()

def add_player_stats(db: Session):
    player_stats = scrape_player_stats(db)
    print(player_stats)
    for player_stat in player_stats:
            
        try:
            db_player_stats = PlayerStat(
                name = player_stat["player_name"],
                sg_total = player_stat["SG: Total"],
                sg_ttg = player_stat["SG: T2G"],
                sg_ott = player_stat["SG: OTT"],
                sg_apr = player_stat["SG: APR"],
                sg_atg = player_stat["SG: ATG"],
                sg_putt = player_stat["SG: PUTT"],
            )

            db.add(db_player_stats)
        except KeyError:
            print(f"No stats for {player_stat['player_name']}")
        db.commit()
    db.refresh(db_player_stats)
    return db_player_stats

