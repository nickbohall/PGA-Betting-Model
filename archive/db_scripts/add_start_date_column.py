from sqlalchemy import text
from app.db.db_setup import engine

def add_start_date_column():
    print("Adding start_date column to tournaments table...")
    
    try:
        # Using SQLAlchemy to execute the ALTER TABLE statement
        with engine.connect() as conn:
            # Check if column already exists to avoid errors
            result = conn.execute(text("PRAGMA table_info(tournaments)"))
            columns = [row[1] for row in result.fetchall()]
            
            if "start_date" not in columns:
                conn.execute(text("ALTER TABLE tournaments ADD COLUMN start_date DATE"))
                conn.commit()
                print("Successfully added start_date column to tournaments table.")
            else:
                print("Column start_date already exists in tournaments table.")
                
    except Exception as e:
        print(f"Error adding start_date column: {e}")
        raise

if __name__ == "__main__":
    add_start_date_column()