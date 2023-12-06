from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Enum, Text
from sqlalchemy.orm import relationship

from ..db.db_setup import Base
from .mixins import Timestamp

from ..models import player

class Schedule(Timestamp, Base):
    __tablename__ = "schedule"
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer)
    finish = Column(Integer)

    tournament_id = Column(Integer, ForeignKey("tournament.id"))
    player_id = Column(String, ForeignKey("player.id"))