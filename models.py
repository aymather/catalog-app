#!/bin/bash/python3
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func

from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
import datetime
Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key = True)
    username = Column(String, nullable = False)
    name = Column(String)
    email = Column(String)
    password = Column(String)
    picture = Column(String)
    main_character = Column(String)
    sign_up_date = Column(DateTime(timezone = True), default = func.now())

    def get_date(self):
        strdate = self.sign_up_date.strftime("%Y/%m/%d")
        year, month, day = strdate.split('/')
        date_array = [int(year), int(month), int(day)]
        return date_array


class Tier(Base):
    __tablename__ = 'tier'
    id = Column(Integer, primary_key = True)
    name = Column(String(32), nullable = False)
    description = Column(String)


class Character(Base):
    __tablename__ = 'character'
    id = Column(Integer, primary_key = True)
    name = Column(String(32), nullable = False)
    character_tier = Column(String(32), ForeignKey('tier.name'))
    tier = relationship(Tier)
    description = Column(String)
    image = Column(String)
    creation_date = Column(DateTime(timezone = True), default = func.now())

    def get_date(self):
        strdate = self.creation_date.strftime("%Y/%m/%d")
        year, month, day = strdate.split('/')
        date_array = [int(year), int(month), int(day)]
        return date_array


class CharacterDiscussion(Base):
    __tablename__ = 'characterdiscussion'
    id = Column(Integer, primary_key = True)
    character = relationship('Character')
    character_id = Column(Integer, ForeignKey('character.id'))
    user = relationship(User)
    username = Column(Integer, ForeignKey('user.username'))
    message = Column(String)
    date = Column(DateTime(timezone = True), default = func.now())

    def get_date(self):
        strdate = self.date.strftime("%Y/%m/%d")
        year, month, day = strdate.split('/')
        date_array = [int(year), int(month), int(day)]
        return date_array


engine = create_engine('sqlite:///ssbmdatabase.db')
Base.metadata.create_all(engine)