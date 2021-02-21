"""DataBase models."""
from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class TelegramUser(Base):
    """Telegram users."""

    __tablename__ = 'telegram_users'

    id = Column(Integer, primary_key=True)

    telegram_id = Column(Integer)
    stories = relationship('Story', back_populates='author')


class Story(Base):
    """Srories."""

    __tablename__ = 'stories'

    id = Column(Integer, primary_key=True)

    name = Column(Text, unique=True)
    author_id = Column(Integer, ForeignKey('telegram_users.id'))
    author = relationship('TelegramUser', back_populates='stories')

    messages = relationship('Message', back_populates='story')


class Message(Base):
    """Messages."""

    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)

    story_id = Column(Integer, ForeignKey('stories.id'))
    story = relationship('Story', back_populates='messages')

    message = Column(Text)
    parent_id = Column(Integer, ForeignKey('messages.id'))
    link = relationship('Message', lazy='joined', join_depth=1)
