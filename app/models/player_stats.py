from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Enum, Text, Float
from sqlalchemy.orm import relationship

from . import master

from .mixins import Timestamp

from ..db.db_setup import Base
from ..models import player

class PlayerStat(Timestamp, Base):
    __tablename__ = "player_stats"
    name = Column(String, primary_key=True, index=True)
    id = Column(String)
    sg_total = Column(Float, nullable=True, default=0.0)
    sg_ttg = Column(Float, nullable=True, default=0.0)
    sg_ott = Column(Float, nullable=True, default=0.0)
    sg_apr = Column(Float, nullable=True, default=0.0)
    sg_atg = Column(Float, nullable=True, default=0.0)
    sg_putt = Column(Float, nullable=True, default=0.0)