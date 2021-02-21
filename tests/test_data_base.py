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
    user = main.get_user_or_make_if_new(2)
    story = main.make_story(user.telegram_id, 'test_make_story')
    expect_story = main.session.query(models.Story).filter_by(
        name='test_make_story',
    ).first()
    assert expect_story is story

    user = main.get_user_or_make_if_new(3)
    with pytest.raises(IntegrityError):
        main.make_story(user.telegram_id, 'test_make_story')


def test_get_story_by_name():
    """Test func get_story_by_name."""
    user = main.get_user_or_make_if_new(4)
    main.make_story(user.telegram_id, 'test_get_story_by_name')
    expect_story = main.session.query(models.Story).filter_by(
        author=user,
        name='test_get_story_by_name',
    ).first()
    story = main.get_user_story_by_name(
        user.telegram_id, 'test_get_story_by_name',
    )
    assert expect_story is story

    user = main.get_user_or_make_if_new(5)
    with pytest.raises(ValueError):
        main.get_user_story_by_name(
            user.telegram_id, 'test_get_story_by_name',
        )
