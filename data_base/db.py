"""Data base app."""
import logging
from logging.config import dictConfig
from os import environ

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI')

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
        },
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
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
