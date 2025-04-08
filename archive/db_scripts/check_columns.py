from app.db.db_setup import engine
from sqlalchemy import text

def check_columns():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("PRAGMA table_info(tournaments)"))
            columns = [row[1] for row in result.fetchall()]
            print(f"Columns in tournaments table: {columns}")
            
            if "start_date" in columns:
                print("start_date column exists in tournaments table.")
            else:
                print("start_date column does NOT exist in tournaments table.")
    except Exception as e:
        print(f"Error checking columns: {e}")

if __name__ == "__main__":
    check_columns()