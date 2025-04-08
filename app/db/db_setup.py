from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()

# Get the project root directory
project_root = Path(__file__).parent.parent.parent

# Use SQLite as the database
# Check if DATABASE_URL is provided in environment variables, otherwise use default SQLite path
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{project_root}/app/db/data/pga_model_data.db")

# Create SQLite engine with appropriate parameters
engine = create_engine(
    DATABASE_URL,
    future=True,  # Allows use of new version
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)

Base = declarative_base()

# DB Utilities
def get_db():
    db = SessionLocal()
    try: 
        yield db
    finally:
        db.close()