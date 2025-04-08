"""
Script to automatically run the PostgreSQL migration without prompting
"""
from app.db.pg_rename_tournament_columns import rename_tournament_columns

if __name__ == "__main__":
    print("Starting automatic PostgreSQL migration")
    rename_tournament_columns()
    print("Migration completed")