from sqlalchemy import Integer, String, ARRAY, Column, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from flask import current_app

Base = declarative_base()


class BaseModel(Base):
    __abstract__ = True
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(String(255))
    updated_by = Column(String(255))

    def __init__(self, created_by=None, updated_by=None):
        self.created_by = created_by or current_app.config.get('DEFAULT_USER')
        self.updated_by = updated_by or current_app.config.get('DEFAULT_USER')


class User(BaseModel):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    username = Column(String)
    email = Column(String)
    password = Column(String)
    profilePicture = Column(String)
    country = Column(String)
    about = Column(String)
    platform = Column(String)
    rank = Column(Integer)
    top3Attacker = Column(ARRAY(Integer))
    top3Defender = Column(ARRAY(Integer))
    hasMic = Column(Integer)
    platformUsername = Column(String)
    discordUsername = Column(String)

    def __init__(self, name, email, password, username=None, profilePicture=None, country=None, about=None,
                 platform=None, rank=None, top3Attacker=None, top3Defender=None, hasMic=None,
                 platformUsername=None, discordUsername=None, created_by=None, updated_by=None):
        super().__init__(created_by, updated_by)
        self.name = name
        self.username = username
        self.email = email
        self.password = password
        self.profilePicture = profilePicture
        self.country = country
        self.about = about
        self.platform = platform
        self.rank = rank
        self.top3Attacker = top3Attacker
        self.top3Defender = top3Defender
        self.hasMic = hasMic
        self.platformUsername = platformUsername
        self.discordUsername = discordUsername

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'username': self.username,
            'email': self.email,
            'profilePicture': self.profilePicture,
            'country': self.country,
            'about': self.about,
            'platform': self.platform,
            'rank': self.rank,
            'top3Attacker': self.top3Attacker,
            'top3Defender': self.top3Defender,
            'hasMic': self.hasMic,
            'platformUsername': self.platformUsername,
            'discordUsername': self.discordUsername
        }


class Operator(Base):
    __tablename__ = 'operators'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    side = Column(String)
    icon = Column(String)

    def __init__(self, name, side, icon, created_by=None, updated_by=None):
        super().__init__(created_by, updated_by)
        self.name = name
        self.side = side
        self.icon = icon

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'side': self.side,
            'icon': self.icon
        }


class Rank(Base):
    __tablename__ = 'ranks'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    value = Column(Integer)
    icon = Column(String)

    def __init__(self, name, icon, value, created_by=None, updated_by=None):
        super().__init__(created_by, updated_by)
        self.name = name
        self.icon = icon
        self.value = value

    def serialize(self):
        return {
            'id': self.id,
            'name': self.name,
            'icon': self.icon,
            'value': self.value
        }
