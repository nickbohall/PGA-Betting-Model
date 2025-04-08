from sqlalchemy import text
from app.db.db_setup import engine

def reset_tournament_table():
    print("Resetting tournament table to include tournament_date column...")
    
    try:
        # Using SQLAlchemy connection to drop the table
        # We only want to drop the tournament table, not all tables
        
        with engine.connect() as conn:
            # Drop the tournament table if it exists
            conn.execute(text("DROP TABLE IF EXISTS tournament"))
            conn.commit()
            print("Tournament table dropped successfully.")
            
            # The table will be recreated with the new schema when the application starts
            print("The tournament table will be recreated with the new schema when the application starts.")
            print("Please restart your application and then rescrape the tournaments.")
                
    except Exception as e:
        print(f"Error resetting tournament table: {e}")
        raise

if __name__ == "__main__":
    reset_tournament_table()