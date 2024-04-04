from sqlalchemy.orm import Session

from app.models.player_stats import PlayerStat
from app.models.master import Master
from app.models.player import Player

from app.services.player_stats_scrape import scrape_player_stats


def get_player_stats(db: Session):
    return db.query(PlayerStat).all()

def get_player_stats_for_tourney(db:Session, tourney):
    return db.query(PlayerStat).filter(Master.tournament == tourney)

def add_or_update_player_stats(db: Session):
    player_stats = scrape_player_stats(db)

    updated_players = []
    added_players = []

    for player_stat in player_stats:
        # Check if player exists in the database
        existing_player = db.query(PlayerStat).filter(PlayerStat.name == player_stat["player_name"]).first()


        if existing_player:
            # Update player statistics
            existing_player.sg_total = player_stat["SG: Total"]
            existing_player.sg_ttg = player_stat["SG: T2G"]
            existing_player.sg_ott = player_stat["SG: OTT"]
            existing_player.sg_apr = player_stat["SG: APR"]
            existing_player.sg_atg = player_stat["SG: ATG"]
            existing_player.sg_putt = player_stat["SG: PUTT"]

            updated_players.append(existing_player)
        else:
            try:
                # Add new player statistics
                db_player_stats = PlayerStat(
                    name=player_stat["player_name"],
                    id =  db.query(Player).filter(Player.name == player_stat["player_name"]).first().id,
                    sg_total=player_stat["SG: Total"],
                    sg_ttg=player_stat["SG: T2G"],
                    sg_ott=player_stat["SG: OTT"],
                    sg_apr=player_stat["SG: APR"],
                    sg_atg=player_stat["SG: ATG"],
                    sg_putt=player_stat["SG: PUTT"],
                )
                db.add(db_player_stats)
                added_players.append(db_player_stats)
            except KeyError:
                print(f"No stats for {player_stat['player_name']}")
        db.commit()
    full_change_list = updated_players + added_players
    print("DB Updating!")
    return player_stats

# def add_player_stats(db: Session):
#     player_stats = scrape_player_stats(db)
#     print(player_stats)
#     for player_stat in player_stats:
            
#         try:
#             db_player_stats = PlayerStat(
#                 name = player_stat["player_name"],
#                 id =  db.query(Player).filter(Player.name == player_stat["player_name"]).first().id,
#                 sg_total = player_stat["SG: Total"],
#                 sg_ttg = player_stat["SG: T2G"],
#                 sg_ott = player_stat["SG: OTT"],
#                 sg_apr = player_stat["SG: APR"],
#                 sg_atg = player_stat["SG: ATG"],
#                 sg_putt = player_stat["SG: PUTT"],
#             )

#             db.add(db_player_stats)
#         except KeyError:
#             print(f"No stats for {player_stat['player_name']}")
#         db.commit()
#     db.refresh(db_player_stats)
#     return db_player_stats

