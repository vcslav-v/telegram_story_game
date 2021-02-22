"""Data base app."""
import logging
from logging.config import dictConfig
from os import environ
from typing import List

from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import sessionmaker

from data_base import models

SQLALCHEMY_DATABASE_URI = (
    'postgresql+psycopg2://postgres:{password}@{db}/postgres'.format(
        db=environ.get('DB'),
        password=environ.get('DB_PASSWORD'),
    )
)

LOGGING_CONFIG = {
    'version': 1,
    'formatters': {
        'standart': {
            'format': '%(asctime)s - %(levelname)s: %(message)s',
        },
    },
    'handlers': {
        'file_handler': {
            'class': 'logging.handlers.RotatingFileHandler',
            'level': 'DEBUG',
            'filename': 'app.log',
            'mode': 'a',
            'maxBytes': 10240,
            'backupCount': 0,
            'formatter': 'standart',
        }
    },
    'loggers': {
        __name__: {
            'handlers': ['file_handler'],
            'level': 'DEBUG',
        },
    },
}

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)

engine = create_engine(SQLALCHEMY_DATABASE_URI)
session = sessionmaker(bind=engine)()


def get_user_or_make_if_new(telegram_id: int) -> models.TelegramUser:
    """Return user if one exist or add new user to db."""
    user = session.query(models.TelegramUser).filter_by(
        telegram_id=telegram_id,
    ).first()
    if user:
        return user

    user = models.TelegramUser(telegram_id=telegram_id)

    session.add(user)
    session.commit()
    return user


def make_story(
    telegram_id: int,
    story_name: str,
) -> models.Story:
    """Make and return new story."""
    logger.info(
        'make a story - tg_id = {tg_id}, str_name = {str_name}'.format(
            tg_id=telegram_id,
            str_name=story_name,
        ),
    )
    user = get_user_or_make_if_new(telegram_id)

    new_story = models.Story(name=story_name, author=user)
    session.add(new_story)
    try:
        session.commit()
    except IntegrityError as exc:
        session.close()
        logger.error(
            (
                'Cant make new story because story exist already. '
                'make a story - tg_id = {tg_id}, str_name = {str_name}'
            ).format(
                tg_id=telegram_id,
                str_name=story_name,
            ),
        )
        raise exc
    return new_story


def get_user_story_by_name(telegram_id: int, story_name: str) -> models.Story:
    """Return story by name."""
    user = get_user_or_make_if_new(telegram_id)
    story = session.query(models.Story).filter_by(
        author=user,
        name=story_name,
    ).first()
    if story:
        return story

    logger.error('Story {name} is not exist for tg_id {tg_id}'.format(
        name=story_name,
        tg_id=user.telegram_id,
    ))
    raise ValueError


def make_chapter(
    telegram_id: int,
    story_name: str,
    chapter_name: str,
    chapter_num: int = -1,
):
    """Make new chapter.

    If chapter_num = -1 chapter get next chapter_num.
    """
    story = get_user_story_by_name(telegram_id, story_name)
    next_number = len(story.chapters)
    if chapter_num < 0 or chapter_num == next_number:
        chapter_num = next_number
    elif chapter_num < next_number:
        _make_place_for_insert_chapter(story.chapters, chapter_num)
    else:
        logger.error('Chapter number bigger than exist numbers')
        raise ValueError('Chapter number bigger than exist numbers')

    new_chapter = models.Chapter(
        name=chapter_name,
        number=chapter_num,
        story=story,
    )
    session.add(new_chapter)
    session.commit()
    return new_chapter


def _make_place_for_insert_chapter(chapters, chapter_num):
    """Insert chapter."""
    sorted_chapters = sorted(chapters, key=lambda chp: chp.number)
    for chapter in sorted_chapters[::-1]:
        if chapter.number < chapter_num:
            break
        chapter.number += 1
