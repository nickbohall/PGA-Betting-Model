from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Enum, Text
from sqlalchemy.orm import relationship

from ..db.db_setup import Base
from .mixins import Timestamp

class Tournament(Timestamp, Base):
    __tablename__ = "tournament"

    tourney_name = Column(String, primary_key=True, index=True)
    tourney_id = Column(String)
    course_name = Column(String)