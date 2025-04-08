"""
Script to add sample tournament data to the SQLite database.
This is useful for testing and development.
"""

import os
import sys
import sqlite3
from datetime import datetime
from app.db.db_setup import engine

# Current timestamp
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Sample tournament data
sample_tournaments = [
    {
        "tournament_name": "PGA National Resort (The Champion)",
        "tournament_id": "pga-national-resort",
        "course_name": "PGA National Resort (The Champion)",
        "year": 2025,
        "tournament_date": "February 27 - March 2, 2025",
        "created_at": now,
        "updated_at": now
    },
    {
        "tournament_name": "Grand Reserve Golf Club",
        "tournament_id": "grand-reserve-golf-club",
        "course_name": "Grand Reserve Golf Club",
        "year": 2025,
        "tournament_date": "March 6-9, 2025",
        "created_at": now,
        "updated_at": now
    },
    {
        "tournament_name": "Arnold Palmer's Bay Hill Club & Lodge",
        "tournament_id": "arnold-palmers-bay-hill",
        "course_name": "Arnold Palmer's Bay Hill Club & Lodge",
        "year": 2025,
        "tournament_date": "March 13-16, 2025",
        "created_at": now,
        "updated_at": now
    },
    {
        "tournament_name": "TPC Sawgrass (THE PLAYERS Stadium Course)",
        "tournament_id": "tpc-sawgrass",
        "course_name": "TPC Sawgrass (THE PLAYERS Stadium Course)",
        "year": 2025,
        "tournament_date": "March 20-23, 2025",
        "created_at": now,
        "updated_at": now
    },
    {
        "tournament_name": "Innisbrook Resort (Copperhead Course)",
        "tournament_id": "innisbrook-resort",
        "course_name": "Innisbrook Resort (Copperhead Course)",
        "year": 2025,
        "tournament_date": "March 27-30, 2025",
        "created_at": now,
        "updated_at": now
    }
]

def add_sample_tournaments():
    """
    Add sample tournament data to the SQLite database.
    """
    print("Adding sample tournaments to SQLite database...")
    
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
            print("Tournament table doesn't exist. Please create the table first.")
            return
        
        # Get the current schema to check available columns
        cursor.execute("PRAGMA table_info(tournament)")
        columns = cursor.fetchall()
        column_names = [col[1] for col in columns]
        
        # Check if we have the tournament_date column
        has_date_column = 'tournament_date' in column_names
        
        # Insert sample tournaments
        for tournament in sample_tournaments:
            if has_date_column:
                cursor.execute("""
                    INSERT INTO tournament (tournament_name, tournament_id, course_name, year, tournament_date, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    tournament["tournament_name"],
                    tournament["tournament_id"],
                    tournament["course_name"],
                    tournament["year"],
                    tournament["tournament_date"],
                    tournament["created_at"],
                    tournament["updated_at"]
                ))
            else:
                cursor.execute("""
                    INSERT INTO tournament (tournament_name, tournament_id, course_name, year, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    tournament["tournament_name"],
                    tournament["tournament_id"],
                    tournament["course_name"],
                    tournament["year"],
                    tournament["created_at"],
                    tournament["updated_at"]
                ))
        
        # Commit the changes
        conn.commit()
        
        # Verify the insertion
        cursor.execute("SELECT id, tournament_name, tournament_id, course_name, year FROM tournament")
        tournaments = cursor.fetchall()
        print(f"Added {len(tournaments)} tournaments to the database:")
        for tournament in tournaments:
            print(f"ID: {tournament[0]}, Name: {tournament[1]}, Tournament ID: {tournament[2]}, Course: {tournament[3]}, Year: {tournament[4]}")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"Error adding sample tournaments: {str(e)}")
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    add_sample_tournaments()
    print("Sample data insertion completed.")