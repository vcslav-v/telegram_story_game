"""Data base app."""
import logging

from data_base import db, models

logger = logging.getLogger(__name__)


def make(
    user_id: int,
    story_name: str,
    chapter_name: str,
    chapter_num: int = -1,
):
    """Make new chapter.

    If chapter_num = -1 chapter get next chapter_num.
    """
    session = db.Session()
    story = session.query(models.Story).filter_by(
        author_id=user_id,
        name=story_name,
    ).first()
    next_number = len(story.chapters)
    if chapter_num < 0 or chapter_num == next_number:
        chapter_num = next_number
    elif chapter_num < next_number:
        _make_place_for_insert_chapter(story.chapters, chapter_num)
    else:
        logger.error('Chapter number bigger than exist numbers')
        raise ValueError('Chapter number bigger than exist numbers')

    new_chapter = models.Chapter(
        name=chapter_name,
        number=chapter_num,
        story=story,
    )
    session.add(new_chapter)
    session.commit()
    chapter_repr = new_chapter.to_dict()
    session.close()
    return chapter_repr


def _make_place_for_insert_chapter(chapters, chapter_num):
    """Insert chapter."""
    sorted_chapters = sorted(chapters, key=lambda chp: chp.number)
    for chapter in sorted_chapters[::-1]:
        if chapter.number < chapter_num:
            break
        chapter.number += 1
