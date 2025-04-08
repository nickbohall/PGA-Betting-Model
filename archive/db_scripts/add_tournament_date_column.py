from sqlalchemy import text
from app.db.db_setup import engine

def add_tournament_date_column():
    print("Adding tournament_date column to tournament table...")
    
    try:
        # Using SQLAlchemy to execute the ALTER TABLE statement
        
        with engine.connect() as conn:
            # Check if column already exists to avoid errors
            result = conn.execute(text("PRAGMA table_info(tournament)"))
            columns = [row[1] for row in result.fetchall()]
            
            if "tournament_date" not in columns:
                conn.execute(text("ALTER TABLE tournament ADD COLUMN tournament_date TEXT"))
                conn.commit()
                print("Successfully added tournament_date column to tournament table.")
            else:
                print("Column tournament_date already exists in tournament table.")
                
    except Exception as e:
        print(f"Error adding tournament_date column: {e}")
        raise

if __name__ == "__main__":
    add_tournament_date_column()