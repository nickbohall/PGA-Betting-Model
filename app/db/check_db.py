"""
Script to check the SQLite database schema for the tournament table.
This will display the current column names and structure.
"""

import os
import sqlite3
from pathlib import Path

# Get the project root directory
from app.db.db_setup import engine

def check_tournament_table():
    """
    Checks the schema of the tournament table in the SQLite database.
    """
    print("Checking tournament table in SQLite database...")
    
    try:
        # Use SQLAlchemy engine to get the database path
        db_url = str(engine.url)
        if db_url.startswith('sqlite:///'):
            db_path = db_url.replace('sqlite:///', '')
            print(f"Database path: {db_path}")
            
            # Connect to the SQLite database
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if the tournament table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tournament'")
            if cursor.fetchone():
                print("Tournament table exists")
                
                # Get the schema of the tournament table
                cursor.execute("PRAGMA table_info(tournament)")
                columns = cursor.fetchall()
                
                print("\nTable schema:")
                for col in columns:
                    # col format: (id, name, type, notnull, default_value, pk)
                    print(f"Column: {col[1]}, Type: {col[2]}, Not Null: {col[3]}, Default: {col[4]}, Primary Key: {col[5]}")
                
                # Count records in the table
                cursor.execute("SELECT COUNT(*) FROM tournament")
                count = cursor.fetchone()[0]
                print(f"\nTotal records in tournament table: {count}")
                
                # Show a sample record if available
                if count > 0:
                    cursor.execute("SELECT * FROM tournament LIMIT 1")
                    sample = cursor.fetchone()
                    
                    # Get column names
                    cursor.execute("PRAGMA table_info(tournament)")
                    column_names = [col[1] for col in cursor.fetchall()]
                    
                    print("\nSample record:")
                    for i, col_name in enumerate(column_names):
                        if i < len(sample):  # Ensure we don't go out of bounds
                            print(f"{col_name}: {sample[i]}")
            else:
                print("Tournament table does not exist")
        else:
            print(f"Not a SQLite database: {db_url}")
            
    except Exception as e:
        print(f"Error checking database: {str(e)}")
    
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    check_tournament_table()