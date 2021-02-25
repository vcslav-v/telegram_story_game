"""Data base app."""
import logging

from data_base import models, schemas
from data_base.services import story
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def make(
    db: Session,
    req_body: schemas.MakeMsg,
) -> models.Message:
    """Make new message."""
    user_story = story.get_check_author(db, req_body)
    new_msg = models.Message(story=user_story)
    if req_body.message:
        new_msg.message = req_body.message
    if req_body.next_message_id:
        req_msg = schemas.GetMsg(
            tg_id=req_body.tg_id,
            story_id=req_body.story_id,
            msg_id=req_body.next_message_id,
        )
        next_message = get(db, req_msg)
        new_msg.link = next_message
    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg


def get(db: Session, req_body: schemas.GetMsg) -> models.Message:
    """Return message by id."""
    msg = db.query(models.Message).filter_by(
        id=req_body.msg_id,
        story_id=req_body.story_id,
    ).first()
    if msg:
        return msg

    err_msg = 'There is not message id - {msg_id} for story {st_id}'.format(
        msg_id=req_body.msg_id,
        st_id=req_body.story_id,
    )
    logger.error(err_msg)
    raise ValueError(err_msg)


def get_check_user(
    db: Session,
    req_body: schemas.GetUserMsg
) -> models.Message:
    """Return message by id."""
    msg = db.query(models.Message).filter_by(
        id=req_body.msg_id,
        story_id=req_body.story_id,
    ).first()
    if msg and msg.story.author.telegram_id == req_body.tg_id:
        return msg

    err_msg = 'There is not message id - {msg_id} for story {st_id}'.format(
        msg_id=req_body.msg_id,
        st_id=req_body.story_id,
    )
    logger.error(err_msg)
    raise ValueError(err_msg)


def rm(db: Session, req_body: schemas.GetUserMsg) -> dict:
    """Remove message by id."""
    msg = get_check_user(db, req_body)
    db.delete(msg)
    db.commit()
    return {'result': 'ok'}


def edit(db: Session, req_body: schemas.EditMsg) -> models.Message:
    """Edit text message by id."""
    msg = get_check_user(db, req_body)
    if req_body.message:
        msg.message = req_body.message
    if req_body.next_message_id:
        next_message = get(db, req_body)
        msg.link = next_message
    db.commit()
    db.refresh(msg)
    return msg
