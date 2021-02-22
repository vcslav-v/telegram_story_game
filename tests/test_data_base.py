"""Tests data_base app."""
import os

import pytest
from sqlalchemy.exc import IntegrityError

os.environ['DB'] = 'localhost:5432'
os.environ['DB_PASSWORD'] = 'mysecretpassword'

from data_base import db_tool, models


def test_get_user_or_make_if_new():
    """Test func get_user_or_make_if_new."""
    user = db_tool.get_user_or_make_if_new(1)
    expect_user = db_tool.session.query(models.TelegramUser).filter_by(
        telegram_id=1,
    ).first()
    assert user is expect_user

    user_same = db_tool.get_user_or_make_if_new(1)
    assert user is user_same


def test_make_story():
    """Test func make_story."""
    user = db_tool.get_user_or_make_if_new(2)
    story = db_tool.make_story(user.telegram_id, 'test_make_story')
    expect_story = db_tool.session.query(models.Story).filter_by(
        name='test_make_story',
    ).first()
    assert expect_story is story

    user = db_tool.get_user_or_make_if_new(3)
    with pytest.raises(IntegrityError):
        db_tool.make_story(user.telegram_id, 'test_make_story')


def test_get_story_by_name():
    """Test func get_story_by_name."""
    user = db_tool.get_user_or_make_if_new(4)
    db_tool.make_story(user.telegram_id, 'test_get_story_by_name')
    expect_story = db_tool.session.query(models.Story).filter_by(
        author=user,
        name='test_get_story_by_name',
    ).first()
    story = db_tool.get_user_story_by_name(
        user.telegram_id, 'test_get_story_by_name',
    )
    assert expect_story is story

    user = db_tool.get_user_or_make_if_new(5)
    with pytest.raises(ValueError):
        db_tool.get_user_story_by_name(
            user.telegram_id, 'test_get_story_by_name',
        )


def test_make_chapter():
    """Test func make_chapter."""
    user = db_tool.get_user_or_make_if_new(6)
    story = db_tool.make_story(user.telegram_id, 'test_make_chapter_story')
    chapter = db_tool.make_chapter(
        user.telegram_id,
        story.name,
        'test_make_chapter_chapter',
    )
    expect_chapter = db_tool.session.query(models.Chapter).filter_by(
        story=story,
        name='test_make_chapter_chapter',
    ).first()
    assert chapter.number == 0
    assert expect_chapter is chapter

    db_tool.make_chapter(
        user.telegram_id,
        story.name,
        'test_make_chapter_chapter_2',
    )
    chapter_ins = db_tool.make_chapter(
        user.telegram_id,
        story.name,
        'test_make_chapter_chapter_3',
        0,
    )
    assert chapter.number == 1
    assert chapter_ins.number == 0
