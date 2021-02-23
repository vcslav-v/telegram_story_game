"""DataBase models."""
from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class TelegramUser(Base):
    """Telegram users."""

    __tablename__ = 'telegram_users'

    id = Column(Integer, primary_key=True)

    telegram_id = Column(Integer, unique=True)
    stories = relationship('Story', back_populates='author')

    def to_dict(self):
        """Represent to dict."""
        return {
            'id': self.id,
            'telegram_id': self.telegram_id,
            'stories': [story.to_dict() for story in self.stories],
        }


class Story(Base):
    """Srories."""

    __tablename__ = 'stories'

    id = Column(Integer, primary_key=True)

    name = Column(Text, unique=True)
    author_id = Column(
        Integer, ForeignKey('telegram_users.id'), nullable=False,
    )
    author = relationship('TelegramUser', back_populates='stories')

    chapters = relationship(
        'Chapter',
        back_populates='story',
        cascade='delete-orphan,delete',
    )

    messages = relationship(
        'Message',
        back_populates='story',
        cascade='delete-orphan,delete',
    )

    def to_dict(self):
        """Represent to dict."""
        return {
            'id': self.id,
            'name': self.name,
            'author_id': self.author_id,
            'chapters': [chapter.to_dict() for chapter in self.chapters],
            'messages': [message.to_dict() for message in self.messages],
        }


class Chapter(Base):
    """Chapters."""

    __tablename__ = 'chapters'

    id = Column(Integer, primary_key=True)

    story_id = Column(
        Integer,
        ForeignKey('stories.id'),
        nullable=False,
    )
    story = relationship(
        'Story',
        back_populates='chapters',
        passive_deletes=True,
    )

    number = Column(Integer, nullable=False)
    name = Column(Text, nullable=False)

    start_message = relationship(
        'Message', uselist=False, back_populates='start_chapter_point_for',
    )

    def to_dict(self):
        """Represent to dict."""
        start_message = (
            self.start_message.to_dict() if self.start_message else None
        )
        return {
            'id': self.id,
            'name': self.name,
            'number': self.number,
            'story_id': self.story_id,
            'start_message': start_message,
        }


class Message(Base):
    """Messages."""

    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)

    story_id = Column(Integer, ForeignKey('stories.id'), nullable=False)
    story = relationship(
        'Story',
        passive_deletes=True,
        back_populates='messages',
    )

    chapter_id = Column(Integer, ForeignKey('chapters.id'))
    start_chapter_point_for = relationship(
        'Chapter',
        back_populates='start_message',
    )

    message = Column(Text)
    parent_id = Column(Integer, ForeignKey('messages.id'))
    link = relationship('Message', lazy='joined', uselist=False, join_depth=1)

    def to_dict(self):
        """Represent to dict."""
        return {
            'id': self.id,
            'story_id': self.story_id,
            'chapter_id': self.chapter_id,
            'message': self.message,
            'link': self.link.id if self.link else None,
        }
