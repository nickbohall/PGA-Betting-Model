from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

import os

# URL_DATABASE = os.environ["DATABASE_URL"]
URL_DATABASE= "postgresql://postgres:Lasallkid0!@localhost:5432/PgaData"

engine = create_engine(
    URL_DATABASE, connect_args={}, future=True # Allows use of new version
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