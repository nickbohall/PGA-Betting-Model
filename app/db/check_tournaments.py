import sqlite3
import os

# Get the absolute path to the database file
db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '../pga_model_data.db')
print(f"Checking database at: {db_path}")

# Connect to the database
conn = sqlite3.connect(db_path)
conn.row_factory = sqlite3.Row  # This enables column access by name
cursor = conn.cursor()

# Check if there are any tournaments in the table
cursor.execute("SELECT COUNT(*) as count FROM tournament")
count = cursor.fetchone()['count']
print(f"Number of tournaments in the database: {count}")

if count > 0:
    # Get all tournaments
    cursor.execute("SELECT * FROM tournament")
    tournaments = cursor.fetchall()
    print("\nTournaments:")
    for tournament in tournaments:
        print(f"ID: {tournament['id']}, Name: {tournament['tourney_name']}, Tournament ID: {tournament['tourney_id']}, Course: {tournament['course_name']}, Year: {tournament['year']}")
else:
    print("No tournaments found in the database.")

# Close the connection
conn.close()