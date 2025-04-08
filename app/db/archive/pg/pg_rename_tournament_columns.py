"""
PostgreSQL Migration script to rename tournament table columns from 'tourney_*' to 'tournament_*'.
This script updates the column names to maintain consistency across the application.
"""

import sys
import os
from datetime import datetime
import psycopg2
from psycopg2 import sql

# Add the parent directory to sys.path to allow importing app modules
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

# Import the database connection string
from app.db.db_setup import URL_DATABASE

def rename_tournament_columns():
    """
    Performs the migration to rename tournament table columns in PostgreSQL:
    1. Checks if the columns already have the correct names
    2. Renames the columns if needed
    """
    print(f"Connecting to database at: {URL_DATABASE}")
    conn = None
    
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(URL_DATABASE)
        cursor = conn.cursor()
        
        print("Starting tournament table column renaming...")
        
        # Check if the tournament table exists
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'tournament')")
        if not cursor.fetchone()[0]:
            print("Tournament table doesn't exist. No migration needed.")
            conn.close()
            return
        
        # Get the current schema
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'tournament'")
        column_names = [col[0] for col in cursor.fetchall()]
        
        # Check if columns have already been renamed
        if 'tournament_name' in column_names and 'tournament_id' in column_names:
            print("Columns have already been renamed. No migration needed.")
            conn.close()
            return
        
        # Check if the old column names exist
        if 'tourney_name' in column_names:
            print("Renaming 'tourney_name' to 'tournament_name'...")
            cursor.execute(sql.SQL("ALTER TABLE tournament RENAME COLUMN tourney_name TO tournament_name"))
        
        if 'tourney_id' in column_names:
            print("Renaming 'tourney_id' to 'tournament_id'...")
            cursor.execute(sql.SQL("ALTER TABLE tournament RENAME COLUMN tourney_id TO tournament_id"))
        
        # Commit the changes
        conn.commit()
        print("Column renaming completed successfully!")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error during migration: {str(e)}")
        print("Rolling back to previous state...")
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    rename_tournament_columns()
    print("Migration script completed.")