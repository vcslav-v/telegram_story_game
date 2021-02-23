"""Data base app."""
import logging

from data_base import db, models, story

logger = logging.getLogger(__name__)


def make(
    user_id: int,
    story_id: int,
    next_message_id: int = -1,
    message: str = '',
) -> dict:
    """Make new message."""
    session = db.Session()
    user_story = story.get_model(session, story_id, user_id)
    new_msg = models.Message(story=user_story)
    if message:
        new_msg.message = message
    if next_message_id > 0:
        next_message = _get_msg_model(session, next_message_id)
        new_msg.link = next_message

    session.add(new_msg)
    session.commit()
    repr_msg = new_msg.to_dict()
    session.close()
    return repr_msg


def _get_msg_model(session, msg_id: int) -> models.Message:
    """Return message by id."""
    msg = session.query(models.Message).filter_by(id=msg_id).first()
    if msg:
        return msg

    err_msg = 'There is not message id - {msg_id}'.format(
        msg_id=msg_id,
    )
    logger.error(err_msg)
    raise ValueError(err_msg)
