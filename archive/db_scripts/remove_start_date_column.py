from sqlalchemy import text
from app.db.db_setup import engine

def remove_start_date_column():
    print("Removing start_date column from tournaments table...")
    
    try:
        # Using SQLAlchemy to execute the ALTER TABLE statement
        with engine.connect() as conn:
            # Check if column exists to avoid errors
            result = conn.execute(text("PRAGMA table_info(tournaments)"))
            columns = [row[1] for row in result.fetchall()]
            
            if "start_date" in columns:
                # SQLite doesn't support DROP COLUMN directly, so we need to:
                # 1. Create a new table without the column
                # 2. Copy data from old table to new table
                # 3. Drop old table
                # 4. Rename new table to old table name
                
                # Create new table without start_date column
                conn.execute(text("""
                    CREATE TABLE tournaments_new (
                        id INTEGER PRIMARY KEY,
                        tournament_name VARCHAR,
                        tournament_id VARCHAR,
                        course_name VARCHAR,
                        year INTEGER,
                        tournament_date VARCHAR,
                        created_at TIMESTAMP,
                        updated_at TIMESTAMP
                    )
                """))
                
                # Copy data from old table to new table
                conn.execute(text("""
                    INSERT INTO tournaments_new
                    SELECT id, tournament_name, tournament_id, course_name, year, tournament_date, created_at, updated_at
                    FROM tournaments
                """))
                
                # Drop old table
                conn.execute(text("DROP TABLE tournaments"))
                
                # Rename new table to old table name
                conn.execute(text("ALTER TABLE tournaments_new RENAME TO tournaments"))
                
                # Recreate indexes
                conn.execute(text("CREATE INDEX ix_tournaments_id ON tournaments (id)"))
                conn.execute(text("CREATE INDEX ix_tournaments_tournament_name ON tournaments (tournament_name)"))
                conn.execute(text("CREATE INDEX ix_tournaments_tournament_id ON tournaments (tournament_id)"))
                conn.execute(text("CREATE INDEX ix_tournaments_year ON tournaments (year)"))
                
                conn.commit()
                print("Successfully removed start_date column from tournaments table.")
            else:
                print("Column start_date does not exist in tournaments table.")
                
    except Exception as e:
        print(f"Error removing start_date column: {e}")
        raise

if __name__ == "__main__":
    remove_start_date_column()