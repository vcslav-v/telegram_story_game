"""DataBase models."""
from sqlalchemy import Column, ForeignKey, Integer, Text, Boolean, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import hashlib

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

    def to_dict(self):
        """Represent to dict."""
        return {
            'id': self.id,
            'name': self.name,
            'author_id': self.author_id,
            'chapters': [chapter.to_dict() for chapter in self.chapters],
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
    uid = Column(Text)

    messages = relationship(
        'Message',
        back_populates='chapter',
        cascade='delete-orphan,delete',
    )

    def make_uid(self):
        self.uid = hashlib.sha224(bytes(f'{self.id}{self.story.author.telegram_id}', 'utf-8')).hexdigest()

    def to_dict(self):
        """Represent to dict."""
        return {
            'id': self.id,
            'name': self.name,
            'number': self.number,
            'story_id': self.story_id,
        }

    def messages_map_to_dict(self):
        """Represent messages."""
        return {
            'id': self.id,
            'name': self.name,
            'story': self.story.name,
            'story_id': self.story.id,
            'messages': [msg.to_dict() for msg in self.messages],
        }


class Message(Base):
    """Messages."""

    __tablename__ = 'messages'

    id = Column(Integer, primary_key=True)

    chapter_id = Column(Integer, ForeignKey('chapters.id'), nullable=False)
    chapter = relationship(
        'Chapter',
        passive_deletes=True,
        back_populates='messages',
    )

    is_start_chapter = Column(Boolean, default=False)
    content_type = Column(Text)
    message = Column(Text)
    media = relationship(
        'Media',
        uselist=False,
        back_populates='parrent_message',
        cascade='delete-orphan,delete',
        foreign_keys='[Media.parrent_message_id]',
    )

    parent_id = Column(Integer, ForeignKey('messages.id'))
    link = relationship('Message', lazy='joined', uselist=False, join_depth=1)

    own_buttons = relationship(
        'Button',
        back_populates='parrent_message',
        cascade='delete-orphan,delete',
        foreign_keys='[Button.parrent_message_id]',
    )

    from_button = relationship(
        'Button',
        back_populates='next_message',
        foreign_keys='[Button.next_message_id]',
    )

    def to_dict(self):
        """Represent to dict."""
        return {
            'id': self.id,
            'content_type': self.content_type,
            'chapter_id': self.chapter_id,
            'message': self.message,
            'media': {'id': self.media.id} if self.media else None,
            'is_start_chapter': self.is_start_chapter,
            'link': self.link.id if self.link else None,
            'parrent': self.parent_id if self.parent_id else None,
            'from_buttons': self.from_button if self.from_button else None,
            'buttons': [btn.to_dict() for btn in self.own_buttons],
        }


class Button(Base):
    """Buttons."""

    __tablename__ = 'buttons'

    id = Column(Integer, primary_key=True)

    text = Column(Text, nullable=False)
    parrent_message_id = Column(
        Integer,
        ForeignKey('messages.id'),
        nullable=False,
    )
    parrent_message = relationship(
        'Message',
        back_populates='own_buttons',
        foreign_keys=[parrent_message_id]
    )

    next_message_id = Column(Integer, ForeignKey('messages.id'))
    next_message = relationship(
        'Message',
        back_populates='from_button',
        foreign_keys=[next_message_id],
    )

    def to_dict(self):
        """Represent to dict."""
        return {
            'id': self.id,
            'text': self.text,
            'parrent_message_id': self.parrent_message_id,
            'next_message_id': (
                self.next_message_id if self.next_message_id else None
            ),
        }


class Media(Base):
    __tablename__ = 'media'

    id = Column(Integer, primary_key=True)
    uid = Column(Text)
    file_data = Column(LargeBinary, nullable=False)
    content_type = Column(Text)
    parrent_message_id = Column(
        Integer,
        ForeignKey('messages.id'),
        nullable=False,
    )
    parrent_message = relationship(
        'Message',
        back_populates='media',
        foreign_keys=[parrent_message_id]
    )

    def make_uid(self):
        self.uid = hashlib.sha224(bytes(f'{self.id}{self.parrent_message.id}', 'utf-8')).hexdigest()