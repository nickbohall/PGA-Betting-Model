"""
SQLite Migration script to rename tournament table columns from 'tourney_*' to 'tournament_*'.
This script updates the column names to maintain consistency across the application.
"""

import sqlite3
import os
from app.db.db_setup import engine

def rename_tournament_columns():
    """
    Performs the migration to rename tournament table columns in SQLite:
    1. Checks if the columns already have the correct names
    2. Renames the columns if needed using SQLite's ALTER TABLE
    """
    print("Starting tournament table column renaming for SQLite...")
    
    # Extract the database path from the engine URL
    db_url = str(engine.url)
    if not db_url.startswith('sqlite:///'):
        print(f"Not a SQLite database: {db_url}")
        return
        
    db_path = db_url.replace('sqlite:///', '')
    print(f"Database path: {db_path}")
    
    conn = None
    try:
        # Connect to the SQLite database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if the tournament table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tournament'")
        if not cursor.fetchone():
            print("Tournament table doesn't exist. No migration needed.")
            return
        
        # Get the current schema
        cursor.execute("PRAGMA table_info(tournament)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Check if columns have already been renamed
        if 'tournament_name' in column_names and 'tournament_id' in column_names:
            print("Columns have already been renamed. No migration needed.")
            return
        
        # SQLite doesn't support direct column renaming like PostgreSQL
        # We need to create a new table with the desired schema, copy data, and replace the old table
        
        # Check if the old column names exist
        needs_migration = 'tourney_name' in column_names or 'tourney_id' in column_names
        
        if needs_migration:
            print("Creating new table with renamed columns...")
            
            # Create column definitions for the new table
            new_columns = []
            old_to_new_mapping = {
                'tourney_name': 'tournament_name',
                'tourney_id': 'tournament_id'
            }
            
            for col in columns:
                col_id, col_name, col_type, not_null, default_val, is_pk = col
                # Replace column name if it's one we want to rename
                if col_name in old_to_new_mapping:
                    new_col_name = old_to_new_mapping[col_name]
                    print(f"Will rename '{col_name}' to '{new_col_name}'")
                else:
                    new_col_name = col_name
                
                # Build the column definition
                col_def = f"{new_col_name} {col_type}"
                if not_null:
                    col_def += " NOT NULL"
                if default_val is not None:
                    col_def += f" DEFAULT {default_val}"
                if is_pk:
                    col_def += " PRIMARY KEY"
                
                new_columns.append(col_def)
            
            # Create the new table
            create_table_sql = f"CREATE TABLE tournament_new ({', '.join(new_columns)})"
            cursor.execute(create_table_sql)
            
            # Map old column names to new ones for the INSERT statement
            insert_columns = []
            for col_name in column_names:
                if col_name in old_to_new_mapping:
                    insert_columns.append(old_to_new_mapping[col_name])
                else:
                    insert_columns.append(col_name)
            
            # Copy data from old table to new table
            cursor.execute(f"INSERT INTO tournament_new SELECT {', '.join(column_names)} FROM tournament")
            
            # Drop the old table
            cursor.execute("DROP TABLE tournament")
            
            # Rename the new table to the original name
            cursor.execute("ALTER TABLE tournament_new RENAME TO tournament")
            
            # Commit the changes
            conn.commit()
            print("Column renaming completed successfully!")
        else:
            print("No columns need to be renamed.")
        
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