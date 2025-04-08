from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Enum, Text, Float
from sqlalchemy.orm import relationship

from ..db.db_setup import Base
from .mixins import Timestamp

from . import player, tournament

class Master(Timestamp, Base):
    __tablename__ = "master"
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer)
    tournament_id = Column(String)
    tournament_name = Column(String)
    course_name = Column(String)
    player_id = Column(String)
    player_name = Column(String)
    finish = Column(Integer, nullable=True)
    score = Column(Integer, nullable=True)
    sg_total = Column(Float, nullable=True)
    sg_ttg = Column(Float, nullable=True)
    sg_ott = Column(Float, nullable=True)
    sg_apr = Column(Float, nullable=True)
    sg_atg = Column(Float, nullable=True)
    sg_putt = Column(Float, nullable=True)
    odds = Column(Integer, nullable=True)

