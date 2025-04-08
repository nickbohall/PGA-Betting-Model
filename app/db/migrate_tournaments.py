"""
Migration script to update the tournament table schema.
This script adds an 'id' column as the primary key and a 'year' column to the tournament table.
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add the parent directory to sys.path to allow importing app modules
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

# Use current year as default
CURRENT_YEAR = datetime.now().year

def migrate_tournament_table():
    """
    Performs the migration of the tournament table:
    1. Creates a backup of the current table
    2. Creates a new table with the updated schema
    3. Copies data from the old table to the new one, adding default values for new columns
    4. Drops the old table and renames the new one
    """
    # Connect to the database - use absolute path
    db_path = os.path.join(os.path.dirname(parent_dir), 'pga_model_data.db')
    print(f"Connecting to database at: {db_path}")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print("Starting tournament table migration...")
    
    try:
        # Check if the tournament table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tournament'")
        if not cursor.fetchone():
            print("Tournament table doesn't exist. Creating new table with updated schema.")
            cursor.execute("""
                CREATE TABLE tournament (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    tournament_name TEXT NOT NULL,
                    tournament_id TEXT,
                    course_name TEXT,
                    year INTEGER,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)
            conn.commit()
            print("Created new tournament table with updated schema.")
            return
        
        # Create a backup of the current table
        print("Creating backup of current tournament table...")
        cursor.execute("CREATE TABLE tournament_backup AS SELECT * FROM tournament")
        conn.commit()
        
        # Get the current schema
        cursor.execute("PRAGMA table_info(tournament)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Check if id and year columns already exist
        has_id = 'id' in column_names
        has_year = 'year' in column_names
        
        if has_id and has_year:
            print("Table already has id and year columns. No migration needed.")
            cursor.execute("DROP TABLE tournament_backup")
            conn.commit()
            return
        
        # Create a new table with the updated schema
        print("Creating new tournament table with updated schema...")
        cursor.execute("""
            CREATE TABLE tournament_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tournament_name TEXT NOT NULL,
                tournament_id TEXT,
                course_name TEXT,
                year INTEGER,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
        """)
        
        # Copy data from the old table to the new one
        print("Copying data to new table with default values for new columns...")
        
        # Get existing columns for the SELECT statement
        select_columns = ", ".join(column_names)
        
        # Prepare the INSERT statement
        insert_columns = ["tournament_name", "tournament_id", "course_name"]
        if "created_at" in column_names:
            insert_columns.append("created_at")
        if "updated_at" in column_names:
            insert_columns.append("updated_at")
            
        placeholders = ["?"] * (len(insert_columns) + 1)  # +1 for the year column
        
        # Get all rows from the old table
        cursor.execute(f"SELECT {select_columns} FROM tournament")
        rows = cursor.fetchall()
        
        # Insert data into the new table
        for row in rows:
            # Create a dictionary to map column names to values
            row_dict = {column_names[i]: row[i] for i in range(len(column_names))}
            
            # Prepare values for insert
            values = []
            for col in insert_columns:
                values.append(row_dict.get(col))
            
            # Add default year value
            values.append(CURRENT_YEAR)
            
            # Insert into new table
            cursor.execute(
                f"INSERT INTO tournament_new ({', '.join(insert_columns)}, year) VALUES ({', '.join(['?'] * len(values))})",
                values
            )
        
        # Drop the old table and rename the new one
        print("Dropping old table and renaming new table...")
        cursor.execute("DROP TABLE tournament")
        cursor.execute("ALTER TABLE tournament_new RENAME TO tournament")
        
        # Create indexes
        print("Creating indexes...")
        cursor.execute("CREATE INDEX idx_tournament_name ON tournament(tournament_name)")
        cursor.execute("CREATE INDEX idx_tournament_id ON tournament(tournament_id)")
        cursor.execute("CREATE INDEX idx_tournament_year ON tournament(year)")
        
        conn.commit()
        print("Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"Error during migration: {str(e)}")
        print("Rolling back to previous state...")
        
        # Check if backup exists and restore it
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tournament_backup'")
        if cursor.fetchone():
            cursor.execute("DROP TABLE IF EXISTS tournament")
            cursor.execute("ALTER TABLE tournament_backup RENAME TO tournament")
            conn.commit()
            print("Restored from backup.")
    
    finally:
        # Clean up backup if it exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tournament_backup'")
        if cursor.fetchone():
            cursor.execute("DROP TABLE tournament_backup")
            conn.commit()
            print("Removed backup table.")
        
        conn.close()

if __name__ == "__main__":
    migrate_tournament_table()
    print("Migration script completed.")