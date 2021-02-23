"""Data base app."""
import logging

from data_base import db, models, story

logger = logging.getLogger(__name__)


def make(
    user_id: int,
    story_id: int,
    chapter_name: str,
    chapter_num: int = -1,
) -> dict:
    """Make new chapter.

    If chapter_num = -1 chapter get next chapter_num.
    """
    session = db.Session()
    user_story = story.get_model(session, story_id, user_id)
    next_number = len(user_story.chapters)
    if chapter_num < 0 or chapter_num == next_number:
        chapter_num = next_number
    elif chapter_num < next_number:
        _make_place_for_insert_chapter(user_story.chapters, chapter_num)
    else:
        logger.error('Chapter number bigger than exist numbers')
        raise ValueError('Chapter number bigger than exist numbers')

    new_chapter = models.Chapter(
        name=chapter_name,
        number=chapter_num,
        story=user_story,
    )
    session.add(new_chapter)
    session.commit()
    chapter_repr = new_chapter.to_dict()
    session.close()
    return chapter_repr


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


def get_model(session, story_id: int, chapter_id: int) -> models.Chapter:
    """Return chapter model."""
    user_chapter = session.query(models.Chapter).filter_by(
        id=chapter_id,
        story_id=story_id,
    ).first()
    if user_chapter:
        return user_chapter
    err_msg = 'Chapter {id} is not exist for story {story_id}'.format(
        id=chapter_id,
        story_id=story_id,
    )
    logger.error(err_msg)
    raise ValueError(err_msg)


def rename(story_id: int, chapter_id: int, new_name: str) -> dict:
    """Rename chapter."""
    session = db.Session()
    story_chapter = get_model(session, story_id, chapter_id)
    if not new_name:
        session.close()
        logger.error('Name "{name}" is not correct.'.format(
            name=new_name,
        ))
        raise ValueError
    story_chapter.name = new_name
    session.commit()
    repr_chapter = story_chapter.to_dict()
    session.close()
    return repr_chapter


def replace(
    user_id: int,
    story_id: int,
    chapter_id: int,
    new_position: int,
) -> dict:
    """Move chapter to new position."""
    session = db.Session()
    user_story = story.get_model(session, story_id, user_id)
    story_chapter = get_model(session, story_id, chapter_id)
    if new_position < 0 or new_position > len(user_story.chapters) - 1:
        session.close()
        err_msg = 'Position {pos} is wrong'.format(pos=new_position)
        logger.error(err_msg)
        raise ValueError(err_msg)
    elif story_chapter.number != new_position:
        _make_place_for_insert_chapter(
            user_story.chapters,
            new_position,
            new=False,
            old_num=story_chapter.number,
        )
    story_chapter.number = new_position
    session.commit()
    repr_chapter = story_chapter.to_dict()
    session.close()
    return repr_chapter
