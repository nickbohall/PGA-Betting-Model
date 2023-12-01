import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from dotenv import load_dotenv

load_dotenv()

URL_DATABASE = 'postgresql://postgres:Lasallkid0!@localhost:5432/PgaData'
# URL_DATABASE = os.getenv['DATABASE_URL']

engine = create_engine(URL_DATABASE)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bine=engine)

Base = declarative_base()