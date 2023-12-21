from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Enum, Text, Float
from sqlalchemy.orm import relationship

from .mixins import Timestamp

from ..db.db_setup import Base
from ..models import schedule, player

class PlayerStat(Timestamp, Base):
    __tablename__ = "player_stats"
    name = Column(String, primary_key=True, index=True)
    sg_total = Column(Float)
    sg_ttg = Column(Float)
    sg_ott = Column(Float)
    sg_apr = Column(Float)
    sg_atg = Column(Float)
    sg_putt = Column(Float)