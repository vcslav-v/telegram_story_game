"""Data base app."""
import logging
from sqlalchemy.orm import Session

from data_base import models, schemas
from data_base.services import story, message

logger = logging.getLogger(__name__)


def make(
    db: Session,
    req_body: schemas.MakeChapter,
) -> models.Chapter:
    """Make new chapter."""
    user_story = story.get_check_author(db, req_body)
    next_number = len(user_story.chapters)
    if not req_body.chapter_num or req_body.chapter_num == next_number:
        position = next_number
    elif -1 < req_body.chapter_num < next_number:
        position = req_body.chapter_num
        _make_place_for_insert_chapter(
            user_story.chapters,
            req_body.chapter_num,
        )
    else:
        logger.error('Wrong chapter number')
        raise ValueError('Wrong chapter number')

    new_chapter = models.Chapter(
        name=req_body.chapter_name,
        number=position,
        story=user_story,
    )
    db.add(new_chapter)
    db.commit()
    new_chapter.make_uid()
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


def get_check_user(
    db: Session,
    req_body: schemas.GetUserChapter,
) -> models.Chapter:
    """Return chapter model."""
    user_chapter = db.query(models.Chapter).filter_by(
        id=req_body.chapter_id,
        story_id=req_body.story_id,
    ).first()
    if user_chapter and (
        user_chapter.story.author.telegram_id == req_body.tg_id
    ):
        return user_chapter
    if not user_chapter:
        err_msg = 'Chapter {id} is not exist for story {story_id}'.format(
            id=req_body.chapter_id,
            story_id=req_body.story_id,
        )
    elif user_chapter.story.author.telegram_id != req_body.tg_id:
        err_msg = 'Story {story_id} - access denied'.format(
            story_id=req_body.story_id,
        )
    logger.error(err_msg)
    raise ValueError(err_msg)


def rename(
    db: Session,
    req_body: schemas.RenameChapter,
) -> models.Chapter:
    """Rename chapter."""
    story_chapter = get_check_user(db, req_body)
    story_chapter.name = req_body.new_name
    db.commit()
    db.refresh(story_chapter)
    return story_chapter


def replace(
    db: Session,
    req_body: schemas.ReplaceChapter,
) -> models.Chapter:
    """Move chapter to new position."""
    story_chapter = get_check_user(db, req_body)
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


def rm(
    db: Session,
    req_body: schemas.GetUserChapter,
) -> dict:
    """Remove chapter."""
    story_chapter = get_check_user(db, req_body)
    next_position = story_chapter.number + 1
    for another_chapter in story_chapter.story.chapters[next_position:]:
        another_chapter.number -= 1
    db.delete(story_chapter)
    db.commit()
    return {'result': 'ok'}


def get_chapter_by_uid(
    db: Session,
    req_body: schemas.GetChapterMap,
) -> models.Chapter:
    """Return all chapter msgs."""
    user_chapter = db.query(models.Chapter).filter_by(
        uid=req_body.chapter_hash,
    ).first()
    if user_chapter:
        return user_chapter
    err_msg = 'Wrong hash'
    logger.error(err_msg)
    raise ValueError(err_msg)


def set_ref_block(
    db: Session,
    req_body: schemas.SetRefBlockChapter,
) -> models.Chapter:
    """Rename chapter."""
    story_chapter = get_check_user(db, req_body)
    for msg in story_chapter.messages:
        msg.referal_block = req_body.ref_block
    db.commit()
    db.refresh(story_chapter)
    return story_chapter
