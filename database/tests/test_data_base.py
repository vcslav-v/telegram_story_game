"""Tests data_base app."""
import os

import pytest
from sqlalchemy.exc import IntegrityError

os.environ['SQLALCHEMY_DATABASE_URI'] = (
    'postgresql+psycopg2://postgres:mysecretpassword@localhost:5432/postgres'
)
from data_base import chapter, db, message, models, story, telegram_user


def test_get_user_or_make_if_new():
    """Test func get_user_or_make_if_new."""
    user = telegram_user.get_or_make_if_new(1)
    session = db.Session()
    expect_user = session.query(models.TelegramUser).filter_by(
        telegram_id=1,
    ).first()
    assert user == expect_user.to_dict()
    db.Session.remove()

    user_same = telegram_user.get_or_make_if_new(1)
    assert user == user_same


def test_make_story():
    """Test func make_story."""
    user = telegram_user.get_or_make_if_new(2)
    user_story = story.make(user['id'], 'test_make_story')
    session = db.Session()
    expect_story = session.query(models.Story).filter_by(
        name='test_make_story',
    ).first()
    assert expect_story.to_dict() == user_story
    db.Session.remove()

    user = telegram_user.get_or_make_if_new(3)
    with pytest.raises(IntegrityError):
        story.make(user['id'], 'test_make_story')

    with pytest.raises(ValueError):
        story.make(10, 'test_make_story_new')


def test_get_story_by_name():
    """Test func get_story_by_name."""
    user = telegram_user.get_or_make_if_new(4)
    user_story = story.make(user['id'], 'test_get_story_by_name')
    session = db.Session()
    expect_story = session.query(models.Story).filter_by(
        author_id=user['id'],
        name='test_get_story_by_name',
    ).first()
    user_story = story.get(
        user['id'],
        user_story['id'],
    )
    assert expect_story.to_dict() == user_story

    user = telegram_user.get_or_make_if_new(5)
    with pytest.raises(ValueError):
        story.get(
            user['id'], user_story['id'],
        )
    db.Session.remove()


def test_make_chapter():
    """Test func make_chapter."""
    user = telegram_user.get_or_make_if_new(6)
    user_story = story.make(user['id'], 'test_make_chapter_story')
    story_chapter = chapter.make(
        user['id'],
        user_story['id'],
        'test_make_chapter_chapter',
    )
    session = db.Session()
    expect_chapter = session.query(models.Chapter).filter_by(
        story_id=user_story['id'],
        name='test_make_chapter_chapter',
    ).first()
    assert story_chapter['number'] == 0
    assert expect_chapter.to_dict() == story_chapter

    chapter.make(
        user['id'],
        user_story['id'],
        'test_make_chapter_chapter_2',
    )
    chapter_ins = chapter.make(
        user['id'],
        user_story['id'],
        'test_make_chapter_chapter_3',
        0,
    )
    moved_chapter = session.query(models.Chapter).filter_by(
        story_id=user_story['id'],
        name='test_make_chapter_chapter',
    ).first()
    assert moved_chapter.number == 1
    assert chapter_ins['number'] == 0
    db.Session.remove()


def test_make_message():
    """Test func make_message."""
    user = telegram_user.get_or_make_if_new(7)
    user_story = story.make(user['id'], 'test_make_message_story')
    chapter.make(
        user['id'],
        user_story['id'],
        'test_make_message_chapter',
    )
    story_message = message.make(
        user['id'],
        user_story['id'],
        message='test_make_message',
    )
    session = db.Session()
    expect_msg = session.query(models.Message).filter_by(
        id=story_message['id'],
    ).first()
    assert expect_msg.to_dict() == story_message

    message_parrent = message.make(
        user['id'],
        user_story['id'],
        message='test_make_message_2',
        next_message_id=story_message['id'],
    )
    assert message_parrent['link'] == expect_msg.to_dict()['id']
    db.Session.remove()


def test_rm_story():
    user = telegram_user.get_or_make_if_new(8)
    user_story = story.make(user['id'], 'test_rm_story')
    story_chapter = chapter.make(
        user['id'],
        user_story['id'],
        'test_rm_story_chapter',
    )
    msg = message.make(
        user['id'],
        user_story['id'],
        message='test_rm_story',
    )
    story.rm(user['id'], user_story['id'])
    session = db.Session()
    expect_story = session.query(models.Story).filter_by(
        id=user_story['id'],
    ).first()
    assert expect_story is None

    expect_chapter = session.query(models.Chapter).filter_by(
        id=story_chapter['id'],
    ).first()
    assert expect_chapter is None

    expect_msg = session.query(models.Message).filter_by(
        id=msg['id'],
    ).first()
    assert expect_msg is None


def test_rename_story():
    user = telegram_user.get_or_make_if_new(9)
    user_story = story.make(user['id'], 'test_rename_story')
    rename_story = story.rename(
        user['id'],
        user_story['id'],
        'rename',
    )
    session = db.Session()
    rnm_story = session.query(models.Story).filter_by(
        id=user_story['id'],
    ).first()
    assert rnm_story.name == 'rename'
    assert rename_story['name'] == rnm_story.name


def test_rename_chapter():
    user = telegram_user.get_or_make_if_new(10)
    user_story = story.make(user['id'], 'test_rename_chapter')
    story_chapter = chapter.make(
        user['id'],
        user_story['id'],
        'test_chapter',
    )
    renamed_chapter = chapter.rename(
        user_story['id'],
        story_chapter['id'],
        'new name',
    )
    session = db.Session()
    real_chapter = session.query(models.Chapter).filter_by(
        id=story_chapter['id'],
    ).first()
    assert real_chapter.name == 'new name'
    assert renamed_chapter['name'] == 'new name'


def test_replace_chapter():
    user = telegram_user.get_or_make_if_new(11)
    user_story = story.make(user['id'], 'test_replace_chapter')
    first_chapter = chapter.make(
        user['id'],
        user_story['id'],
        'test_replace_chapter_0',
    )
    chapter.make(
        user['id'],
        user_story['id'],
        'test_replace_chapter_1',
    )
    chapter.make(
        user['id'],
        user_story['id'],
        'test_replace_chapter_2',
    )
    chapter.make(
        user['id'],
        user_story['id'],
        'test_replace_chapter_3',
    )

    replased_chapter = chapter.replace(
        user['id'],
        user_story['id'],
        first_chapter['id'],
        3,
    )
    session = db.Session()
    real_chapter = session.query(models.Chapter).filter_by(
        id=replased_chapter['id'],
    ).first()
    assert real_chapter.number == 3
    assert replased_chapter['number'] == 3
    replased_chapter = chapter.replace(
        user['id'],
        user_story['id'],
        first_chapter['id'],
        0,
    )
    real_chapter = session.query(models.Chapter).filter_by(
        id=replased_chapter['id'],
    ).first()
    assert real_chapter.number == 0
    assert replased_chapter['number'] == 0
    real_story = session.query(models.Story).filter_by(
        id=user_story['id'],
    ).first()
    sorted_chapters = sorted(real_story.chapters, key=lambda chp: chp.number)
    for index in range(3):
        assert sorted_chapters[index].number == index