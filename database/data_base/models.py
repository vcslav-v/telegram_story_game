"""DataBase models."""
from sqlalchemy import Column, ForeignKey, Integer, Text, Boolean, LargeBinary
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import hashlib
import random
from datetime import datetime

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
    uid = Column(Text, unique=True)
    author_id = Column(
        Integer, ForeignKey('telegram_users.id'), nullable=False,
    )
    author = relationship('TelegramUser', back_populates='stories')
    base_timeout = Column(Integer, default=4)
    k_timeout = Column(Integer, default=200)
    chapters = relationship(
        'Chapter',
        back_populates='story',
        cascade='delete-orphan,delete',
    )

    wait_reactions = relationship(
        'WaitReaction',
        back_populates='story',
        cascade='delete-orphan,delete'
    )

    def make_uid(self):
        self.uid = hashlib.sha224(bytes(f'{datetime.timestamp(datetime.utcnow())}{self.id}', 'utf-8')).hexdigest() 

    def to_dict(self):
        """Represent to dict."""
        return {
            'id': self.id,
            'uid': self.uid,
            'name': self.name,
            'base_timeout': self.base_timeout,
            'k_timeout': self.k_timeout,
            'author_id': self.author_id,
            'is_reactions': True if self.wait_reactions else False,
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

    link_id = Column(Integer, ForeignKey('messages.id'))

    parents = relationship('Message', lazy='joined', join_depth=1, foreign_keys='[Message.link_id]')

    timeout = Column(Integer)
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

    wait_reaction_id = Column(Integer, ForeignKey('wait_reactions.id'))
    wait_reaction = relationship('WaitReaction')

    referal_block = Column(Integer, default=0)

    def to_dict(self):
        """Represent to dict."""
        btns = [btn.to_dict() for btn in self.own_buttons]
        return {
            'id': self.id,
            'content_type': self.content_type,
            'story_id': self.chapter.story_id,
            'chapter_id': self.chapter_id,
            'timeout': self.timeout,
            'message': self.message,
            'media_id': self.media.id if self.media else None,
            'is_start_chapter': self.is_start_chapter,
            'link': self.link_id,
            'parents': [parent.id for parent in self.parents] if self.parents else None,
            'from_buttons': self.from_button if self.from_button else None,
            'buttons': sorted(btns, key=lambda x: x['number']),
            'wait_reaction': self.wait_reaction.to_dict() if self.wait_reaction else {},
            'referal_block': self.referal_block,
        }

    def to_engine_dict(self):
        btns = [btn.to_engine_dict() for btn in self.own_buttons]
        return {
            'id': self.id,
            'content_type': self.content_type,
            'chapter_id': self.chapter_id,
            'speed_type': self.chapter.story.k_timeout,
            'timeout': self.timeout,
            'text': self.message,
            'media_uid': self.media.uid if self.media else None,
            'link': self.link_id,
            'buttons': sorted(btns, key=lambda x: x['number']),
            'wait_reaction_uid': self.wait_reaction.uid if self.wait_reaction else None,
            'referal_block': self.referal_block,
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
    number = Column(Integer)
    parrent_message = relationship(
        'Message',
        back_populates='own_buttons',
        foreign_keys=[parrent_message_id],
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
            'number': self.number,
            'parrent_message_id': self.parrent_message_id,
            'next_message_id': (
                self.next_message_id if self.next_message_id else None
            ),
        }

    def to_engine_dict(self):
        return {
            'text': self.text,
            'number': self.number,
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
        self.uid = hashlib.sha224(bytes(f'{self.file_data}', 'utf-8')).hexdigest()


class WaitReaction(Base):
    __tablename__ = 'wait_reactions'

    id = Column(Integer, primary_key=True)
    uid = Column(Text)
    name = Column(Text)
    reactions = relationship(
        'Reactions',
        back_populates='wait_reaction',
        cascade='delete-orphan,delete',
    )

    story_id = Column(
        Integer,
        ForeignKey('stories.id'),
        nullable=False,
    )
    story = relationship(
        'Story',
        back_populates='wait_reactions',
        passive_deletes=True,
    )

    messages = relationship('Message', back_populates='wait_reaction')

    def make_uid(self):
        reactions = ''.join([react.message for react in self.reactions])
        self.uid = hashlib.sha224(bytes(f'{reactions}', 'utf-8')).hexdigest()

    def to_dict(self):
        return {
            'name': self.name,
            'id': self.id,
        }
    
    def full_to_dict(self):
        return {
            'name': self.name,
            'uid': self.uid,
            'messages': [msg.message for msg in self.reactions] if self.reactions else [],
        }


class Reactions(Base):
    __tablename__ = 'reactions'

    id = Column(Integer, primary_key=True)
    message = Column(Text)
    wait_reaction_id = Column(
        Integer,
        ForeignKey('wait_reactions.id'),
    )
    wait_reaction = relationship(
        'WaitReaction',
        back_populates='reactions',
        passive_deletes=True,
    )
