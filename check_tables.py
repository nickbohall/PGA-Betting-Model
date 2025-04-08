from app.db.db_setup import engine
from sqlalchemy import inspect, text

def check_tables():
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    print(f"Tables in database: {table_names}")
    
    # Print table columns for each table
    for table_name in table_names:
        columns = inspector.get_columns(table_name)
        print(f"\nColumns in {table_name} table:")
        for column in columns:
            print(f"  {column['name']} ({column['type']})")
    
    # Check if players table exists and has data
    if 'players' in table_names:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM players"))
            count = result.scalar()
            print(f"Number of records in players table: {count}")
    else:
        print("players table does not exist")
    
    # Check if tournaments table exists and has data
    if 'tournaments' in table_names:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM tournaments"))
            count = result.scalar()
            print(f"Number of records in tournaments table: {count}")
    else:
        print("tournaments table does not exist")
    
    # Check if player_stats table exists and has data
    if 'player_stats' in table_names:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM player_stats"))
            count = result.scalar()
            print(f"Number of records in player_stats table: {count}")
    else:
        print("player_stats table does not exist")

if __name__ == "__main__":
    check_tables()