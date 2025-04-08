from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Enum, Text
from sqlalchemy.orm import relationship

from ..db.db_setup import Base
from .mixins import Timestamp

class Tournament(Timestamp, Base):
    __tablename__ = "tournaments"

    id = Column(Integer, primary_key=True, index=True)
    tournament_name = Column(String, index=True)
    tournament_id = Column(String, index=True)
    course_name = Column(String)
    year = Column(Integer, index=True)
    tournament_date = Column(String, nullable=True)