from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Enum, Text
from sqlalchemy.orm import relationship

from .mixins import Timestamp

from ..db.db_setup import Base
from ..models import schedule


class Player(Timestamp, Base):
    __tablename__ = "player"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    nationality = Column(String)

    player_stats = relationship("PlayerStats", back_populates="player", uselist=False) # Defines 1:1 relationship
    schedule = relationship("Schedule", back_populates="player")

class PlayerStats(Timestamp, Base):
    __tablename__ = "player_stats"
    id = Column(String, primary_key=True, index=True)
    sg_total = Column(Integer)
    sg_ttg = Column(Integer)
    sg_ott = Column(Integer)
    sg_apr = Column(Integer)
    sg_atg = Column(Integer)
    sg_putt = Column(Integer)
    player_id = Column(String, ForeignKey("player.id"), nullable=False)

    player = relationship("Player", back_populates="player_stats")