"""
Script to run the database migration to update tournament column names.
This will update the database schema to use consistent naming conventions.
"""

import os
import sys
from datetime import datetime

# Add the parent directory to sys.path to allow importing app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)

# Import the migration script
from app.db.rename_tournament_columns import rename_tournament_columns

if __name__ == "__main__":
    print(f"Starting migration at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("This will update the tournament table to use consistent column naming.")
    print("Make sure you have a backup of your database before proceeding.")
    
    confirm = input("Do you want to proceed with the migration? (y/n): ")
    if confirm.lower() in ['y', 'yes']:
        rename_tournament_columns()
        print("Migration completed successfully!")
    else:
        print("Migration cancelled.")