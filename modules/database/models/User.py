from sqlalchemy import Column, Text, Integer, Boolean, DateTime
from modules.global_init import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, unique=True)
    username = Column(Text, nullable=True)
    coming_date = Column(DateTime, nullable=True)
    is_admin = Column(Boolean, nullable=True)
    faceit_id = Column(Text, nullable=True)
    faceit_username = Column(Text, nullable=True)
    last_seen_date = Column(DateTime, nullable=True)
    lang = Column(Text, default='en')
