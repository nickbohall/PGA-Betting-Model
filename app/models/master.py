from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Enum, Text, Float
from sqlalchemy.orm import relationship

from ..db.db_setup import Base
from .mixins import Timestamp

from . import player, tournament

class Master(Timestamp, Base):
    __tablename__ = "master"
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer)
    tourney_id = Column(String)
    tournament_name = Column(String)
    course_name = Column(String)
    player_id = Column(String)
    player_name = Column(String)
    finish = Column(Integer)
    score = Column(Integer)
    sg_total = Column(Float)
    sg_ttg = Column(Float)
    sg_ott = Column(Float)
    sg_apr = Column(Float)
    sg_atg = Column(Float)
    sg_putt = Column(Float)

