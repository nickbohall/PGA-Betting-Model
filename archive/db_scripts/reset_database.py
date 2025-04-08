import os
import sqlite3
from sqlalchemy import create_engine, text
from app.db.db_setup import URL_DATABASE, Base, engine
from app.models import tournament as tournamentmodel
from app.models import player as playermodel
from app.models import player_stats as player_statsmodel
from app.models import master as masteremodel

def reset_database():
    print("Resetting database tables...")
    
    try:
        # Drop the tournament table
        print("Dropping tournament table...")
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE IF EXISTS tournament"))
            conn.commit()
        
        # Recreate all tables
        print("Recreating tables with updated schema...")
        playermodel.Base.metadata.create_all(bind=engine)
        player_statsmodel.Base.metadata.create_all(bind=engine)
        masteremodel.Base.metadata.create_all(bind=engine)
        tournamentmodel.Base.metadata.create_all(bind=engine)
        
        print("Database reset complete. Tables have been recreated with the updated schema.")
        print("You can now restart your application and rescrape the tournaments.")
                
    except Exception as e:
        print(f"Error resetting database: {e}")
        raise

if __name__ == "__main__":
    reset_database()