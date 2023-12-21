from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Enum, Text
from sqlalchemy.orm import relationship

from ..db.db_setup import Base
from .mixins import Timestamp

class Tournament(Timestamp, Base):
    __tablename__ = "tournament"
    name = Column(String, primary_key=True, index=True)
    id = Column(String)