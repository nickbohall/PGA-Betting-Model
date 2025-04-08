"""
Script to check the PostgreSQL database schema for the tournament table.
This will display the current column names and structure.
"""

import sys
import os
import psycopg2

# Add the parent directory to sys.path to allow importing app modules
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(parent_dir)

# Import the database connection string
from app.db.db_setup import URL_DATABASE

def check_tournament_table():
    """
    Checks the schema of the tournament table in the PostgreSQL database.
    """
    print(f"Connecting to database at: {URL_DATABASE}")
    
    try:
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(URL_DATABASE)
        cursor = conn.cursor()
        
        # Check if the tournament table exists
        cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'tournament')")
        if cursor.fetchone()[0]:
            print("Tournament table exists")
            
            # Get the schema of the tournament table
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'tournament'
                ORDER BY ordinal_position
            """)
            columns = cursor.fetchall()
            
            print("\nTable schema:")
            for col in columns:
                print(f"Column: {col[0]}, Type: {col[1]}, Nullable: {col[2]}, Default: {col[3]}")
            
            # Count records in the table
            cursor.execute("SELECT COUNT(*) FROM tournament")
            count = cursor.fetchone()[0]
            print(f"\nTotal records in tournament table: {count}")
            
            # Show a sample record if available
            if count > 0:
                cursor.execute("SELECT * FROM tournament LIMIT 1")
                sample = cursor.fetchone()
                print("\nSample record:")
                cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'tournament' ORDER BY ordinal_position")
                column_names = [col[0] for col in cursor.fetchall()]
                for i, col_name in enumerate(column_names):
                    print(f"{col_name}: {sample[i]}")
        else:
            print("Tournament table does not exist")
        
    except Exception as e:
        print(f"Error checking database: {str(e)}")
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_tournament_table()