"""Data base app."""
import logging

from sqlalchemy.exc import IntegrityError

from data_base import db, models

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

    user = _get_user_model(session, user_id)

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


def get(user_id: int, story_name: str) -> dict:
    """Return story by name."""
    session = db.Session()
    user = session.query(models.TelegramUser).filter_by(
        id=user_id,
    ).first()
    story = session.query(models.Story).filter_by(
        author=user,
        name=story_name,
    ).first()

    if story:
        repr_story = story.to_dict()
        session.close()
        return repr_story

    session.close()
    logger.error('Story {name} is not exist for tg_id {user_id}'.format(
        name=story_name,
        user_id=user_id,
    ))
    raise ValueError


def _get_user_model(session, user_id):
    user = session.query(models.TelegramUser).filter_by(
        id=user_id,
    ).first()
    if not user:
        session.close()
        err_msg = 'Cant make story user id-{user_id} is not exist.'.format(
            user_id=user_id,
        )
        logger.error(err_msg)
        raise ValueError(err_msg)
    return user
