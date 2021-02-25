"""Data base app."""
import logging
from sqlalchemy.orm import Session

from data_base import models, schemas
from data_base.services import story

logger = logging.getLogger(__name__)


def make(
    db: Session,
    req_body: schemas.MakeChapter,
) -> models.Chapter:
    """Make new chapter."""
    user_story = story.get(db, req_body)
    next_number = len(user_story.chapters)
    if not req_body.chapter_num or req_body.chapter_num == next_number:
        position = next_number
    elif req_body.chapter_num < next_number:
        position = req_body.chapter_num
        _make_place_for_insert_chapter(
            user_story.chapters,
            req_body.chapter_num,
        )
    else:
        logger.error('Chapter number bigger than exist numbers')
        raise ValueError('Chapter number bigger than exist numbers')

    new_chapter = models.Chapter(
        name=req_body.chapter_name,
        number=position,
        story=user_story,
    )
    db.add(new_chapter)
    db.commit()
    db.refresh(new_chapter)
    return new_chapter


def _make_place_for_insert_chapter(
    chapters,
    chapter_num,
    new=True,
    old_num=-1,
):
    """Insert chapter."""
    sorted_chapters = sorted(chapters, key=lambda chp: chp.number)
    if new:
        sorted_chapters = sorted_chapters[chapter_num:]
        offer = 1
    elif old_num >= 0:
        if old_num > chapter_num:
            sorted_chapters = sorted_chapters[chapter_num:old_num]
            offer = 1
        elif old_num < chapter_num:
            sorted_chapters = sorted_chapters[old_num + 1:chapter_num + 1]
            offer = -1
        else:
            sorted_chapters = []
            offer = 0
    for chapter in sorted_chapters:
        chapter.number += offer


def get(
    db: Session,
    req_body: schemas.GetChapter,
) -> models.Chapter:
    """Return chapter model."""
    user_chapter = db.query(models.Chapter).filter_by(
        id=req_body.chapter_id,
        story_id=req_body.story_id,
    ).first()
    if user_chapter:
        return user_chapter
    err_msg = 'Chapter {id} is not exist for story {story_id}'.format(
        id=req_body.chapter_id,
        story_id=req_body.story_id,
    )
    logger.error(err_msg)
    raise ValueError(err_msg)


def rename(
    db: Session,
    req_body: schemas.RenameChapter,
) -> models.Chapter:
    """Rename chapter."""
    story_chapter = get(db, req_body)
    story_chapter.name = req_body.new_name
    db.commit()
    db.refresh(story_chapter)
    return story_chapter


def replace(
    db: Session,
    req_body: schemas.ReplaceChapter,
) -> models.Chapter:
    """Move chapter to new position."""
    story_chapter = get(db, req_body)
    chapters = story_chapter.story.chapters
    if req_body.new_num < 0 or req_body.new_num > len(chapters) - 1:
        err_msg = 'Position {pos} is wrong'.format(pos=req_body.new_num)
        logger.error(err_msg)
        raise ValueError(err_msg)
    elif story_chapter.number != req_body.new_num:
        _make_place_for_insert_chapter(
            chapters,
            req_body.new_num,
            new=False,
            old_num=story_chapter.number,
        )
    story_chapter.number = req_body.new_num
    db.commit()
    db.refresh(story_chapter)
    return story_chapter


# TODO rm
# TODO set_start message