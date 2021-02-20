"""DataBase models."""
from sqlalchemy import Column, Integer
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class TelegramUsers(Base):
    """Telegram users."""

    __tablename__ = 'telegram_users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer)


class Stories(Base):
    """Srories."""

    __tablename__ = 'stories'

    id = Column(Integer, primary_key=True)


class Messages(Base):
    """Messages."""

    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)
