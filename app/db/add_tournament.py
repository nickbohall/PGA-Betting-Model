import os
import sys
import psycopg2
from datetime import datetime

# Add the parent directory to sys.path to allow importing app modules
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(current_dir))
sys.path.append(parent_dir)

from app.db.db_setup import URL_DATABASE

# Extract connection parameters from the SQLAlchemy URL
# Format: postgresql://username:password@host:port/database
db_url = URL_DATABASE.replace('postgresql://', '')
username_password, host_port_db = db_url.split('@')
username, password = username_password.split(':')
host_port, database = host_port_db.split('/')
host, port = host_port.split(':')

print(f"Connecting to PostgreSQL database: {database} on {host}:{port}")

# Connect to the database
conn = psycopg2.connect(
    host=host,
    port=port,
    database=database,
    user=username,
    password=password
)
cursor = conn.cursor()

# Current timestamp
now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Sample tournament data
sample_tournaments = [
    {
        "tournament_name": "PGA National Resort (The Champion)",
        "tournament_id": "pga-national-resort",
        "course_name": "PGA National Resort (The Champion)",
        "year": 2025,
        "created_at": now,
        "updated_at": now
    },
    {
        "tournament_name": "Grand Reserve Golf Club",
        "tournament_id": "grand-reserve-golf-club",
        "course_name": "Grand Reserve Golf Club",
        "year": 2025,
        "created_at": now,
        "updated_at": now
    },
    {
        "tournament_name": "Arnold Palmer's Bay Hill Club & Lodge",
        "tournament_id": "arnold-palmers-bay-hill",
        "course_name": "Arnold Palmer's Bay Hill Club & Lodge",
        "year": 2025,
        "created_at": now,
        "updated_at": now
    },
    {
        "tournament_name": "TPC Sawgrass (THE PLAYERS Stadium Course)",
        "tournament_id": "tpc-sawgrass",
        "course_name": "TPC Sawgrass (THE PLAYERS Stadium Course)",
        "year": 2025,
        "created_at": now,
        "updated_at": now
    },
    {
        "tournament_name": "Innisbrook Resort (Copperhead Course)",
        "tournament_id": "innisbrook-resort",
        "course_name": "Innisbrook Resort (Copperhead Course)",
        "year": 2025,
        "created_at": now,
        "updated_at": now
    }
]

# Insert sample tournaments
for tournament in sample_tournaments:
    cursor.execute("""
        INSERT INTO tournament (tournament_name, tournament_id, course_name, year, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s)
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

# Close the connection
conn.close()