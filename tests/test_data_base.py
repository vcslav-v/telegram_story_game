"""Tests data_base app."""
import os

import pytest
from sqlalchemy.exc import IntegrityError

os.environ['DB'] = 'localhost:5432'
os.environ['DB_PASSWORD'] = 'mysecretpassword'

from data_base import main, models


def test_get_user_or_make_if_new():
    """Test func get_user_or_make_if_new."""
    user = main.get_user_or_make_if_new(1)
    expect_user = main.session.query(models.TelegramUser).filter_by(
        telegram_id=1,
    ).first()
    assert user is expect_user

    user_same = main.get_user_or_make_if_new(1)
    assert user is user_same


def test_make_story():
    """Test func make_story."""
    user = main.get_user_or_make_if_new(1)
    story = main.make_story(user.telegram_id, 'test_name')
    expect_story = main.session.query(models.Story).filter_by(
        name='test_name',
    ).first()
    assert expect_story is story

    user = main.get_user_or_make_if_new(2)
    with pytest.raises(IntegrityError):
        main.make_story(user.telegram_id, 'test_name')
