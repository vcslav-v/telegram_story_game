"""Data base app."""
import logging

from sqlalchemy.exc import IntegrityError

from data_base import db, models, telegram_user

logger = logging.getLogger(__name__)


def make(
    user_id: int,
    story_name: str,
) -> dict:
    """Make and return new story."""
    logger.info(
        'make a story - user_id = {user_id}, str_name = {str_name}'.format(
            user_id=user_id,
            str_name=story_name,
        ),
    )
    session = db.Session()

    user = telegram_user.get_model(session, user_id)

    new_story = models.Story(name=story_name, author=user)

    session.add(new_story)
    try:
        session.commit()
    except IntegrityError as exc:
        session.close()
        logger.error(
            (
                'Cant make new story because story exist already. '
                'make a story - tg_id = {user_id}, str_name = {str_name}'
            ).format(
                user_id=user_id,
                str_name=story_name,
            ),
        )
        raise exc
    repr_story = new_story.to_dict()
    session.close()
    return repr_story


def get(user_id: int, story_id: int) -> dict:
    """Return story by name."""
    session = db.Session()
    user = telegram_user.get_model(session, user_id)
    story = session.query(models.Story).filter_by(
        author=user,
        id=story_id,
    ).first()

    if story:
        repr_story = story.to_dict()
        session.close()
        return repr_story

    session.close()
    logger.error('Story {id} is not exist for user {user_id}'.format(
        id=story_id,
        user_id=user_id,
    ))
    raise ValueError


def get_model(session, story_id: int, user_id: int) -> models.Story:
    """Find user's story."""
    story = session.query(models.Story).filter_by(
        author_id=user_id,
        id=story_id,
    ).first()
    if story:
        return story
    session.close()
    logger.error('Story {id} is not exist for user {user_id}'.format(
        id=story_id,
        user_id=user_id,
    ))
    raise ValueError


def rm(user_id: int, story_id: int):
    """Delete story with chapter and mesages."""
    session = db.Session()
    user_story = get_model(session, story_id, user_id)
    session.delete(user_story)
    session.commit()
    session.close()
