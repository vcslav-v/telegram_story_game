"""Data base app."""
import logging
from logging.config import dictConfig
from os import environ

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

if environ.get('DB_URL'):
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{password}@{host}/{dbname}'.format(
        user='postgres',
        password=environ.get('DB_PASSWORD'),
        host=environ.get('DB_URL'),
        dbname='postgres',
    )
else:
    SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://{user}:{password}@{host}/{dbname}'.format(
        user='postgres',
        password='mysecretpassword',
        host='0.0.0.0',
        dbname='postgres',
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

engine = create_engine(
    SQLALCHEMY_DATABASE_URI,
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
