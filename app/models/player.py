from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Enum, Text
from sqlalchemy.orm import relationship

from .mixins import Timestamp

from ..db.db_setup import Base
from ..models import schedule, player_stats


class Player(Timestamp, Base):
    __tablename__ = "player"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    nationality = Column(String)