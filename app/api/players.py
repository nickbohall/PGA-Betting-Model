import fastapi

router = fastapi.APIRouter()

@router.post("/players")
async def add_players(player: SchemaPlayer, db: db_dependency):
    player_info = PgaScrape().get_player_info()
    for player in player_info:
        print(player)
        ind_player = Player(id=player["id"], name=player["name"], nationality=player["nationality"])
        try: 
            db.add(ind_player)
        except sqlalchemy.exc.IntegrityError as sqla_error:
            pass
    db.commit()

@router.get("/players")
def get_players(db: db_dependency):
    result = db.query(Player).all()
    if not result:
        raise HTTPException(status_code=404, detail='players not found')
    return result