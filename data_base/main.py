"""Data base app."""
from os import environ

from sqlalchemy import create_engine

SQLALCHEMY_DATABASE_URI = (
    'postgresql+psycopg2://postgres:{password}@{db}/postgres'.format(
        db=environ.get('DB'),
        password=environ.get('DB_PASSWORD'),
    )
)

engine = create_engine(SQLALCHEMY_DATABASE_URI)
