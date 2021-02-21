"""Data base app."""
import logging
from logging.config import dictConfig
from os import environ

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
