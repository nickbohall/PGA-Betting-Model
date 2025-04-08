import os
import sys
from sqlalchemy import text
from app.db.db_setup import engine, Base
from app.models import tournament, player, player_stats, master

def reset_database():
    """
    Drop all tables and recreate them based on SQLAlchemy models.
    """
    print("Connecting to database...")
    
    try:
        # Drop all tables
        print("Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("All tables dropped successfully.")
        
        # Create all tables
        print("Creating all tables...")
        Base.metadata.create_all(bind=engine)
        print("All tables created successfully.")
        
        print("Database reset complete!")
        return True
    except Exception as e:
        print(f"Error resetting database: {str(e)}")
        return False

if __name__ == "__main__":
    # Add the parent directory to sys.path to allow importing app modules
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(os.path.dirname(current_dir))
    sys.path.append(parent_dir)
    
    # Ask for confirmation
    confirm = input("This will delete all data in the database. Are you sure? (y/n): ")
    if confirm.lower() != 'y':
        print("Operation cancelled.")
        sys.exit(0)
    
    success = reset_database()
    if success:
        print("Database has been reset successfully.")
    else:
        print("Failed to reset database.")