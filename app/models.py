from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class Player(Base):
    __tablename__ = "player"
    id = Column(String, primary_key=True, index=True)
    name = Column(String)
    nationality = Column(String)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

class Tournament(Base):
    __tablename__ = "tournament"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())

class Schedule(Base):
    __tablename__ = "schedule"
    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer)
    finish = Column(Integer)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())
    tournament_id = Column(Integer, ForeignKey("tournament.id"))
    player_id = Column(String, ForeignKey("player.id"))

class PlayerStats(Base):
    __tablename__ = "player_stats"
    id = Column(String, primary_key=True, index=True)
    sg_total = Column(Integer)
    sg_ttg = Column(Integer)
    sg_ott = Column(Integer)
    sg_apr = Column(Integer)
    sg_atg = Column(Integer)
    sg_putt = Column(Integer)
    time_created = Column(DateTime(timezone=True), server_default=func.now())
    time_updated = Column(DateTime(timezone=True), onupdate=func.now())