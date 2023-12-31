from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Enum, Text
from sqlalchemy.orm import relationship

from ..db.db_setup import Base
from .mixins import Timestamp

from ..models import player, tournament

class Schedule(Timestamp, Base):
    __tablename__ = "schedule"
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer)
    tourney_id = Column(String)
    tournament_name = Column(String)
    player_id = Column(String)
    player_name = Column(String)
    finish = Column(Integer)
    score = Column(Integer)

