"""Data base app."""
import logging
from typing import Optional

from data_base import models, schemas
from data_base.services import chapter
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def make(
    db: Session,
    req_body: schemas.MakeMsg,
) -> models.Message:
    """Make new message."""
    user_chapter = chapter.get_check_user(db, req_body)
    new_msg = models.Message(
        chapter=user_chapter,
        content_type=req_body.content_type,
    )
    if req_body.message:
        new_msg.message = req_body.message
    if req_body.next_message_id:
        req_msg = schemas.GetUserMsg(
            tg_id=req_body.tg_id,
            story_id=req_body.story_id,
            msg_id=req_body.next_message_id,
        )
        next_message = get_check_user(db, req_msg)
        new_msg.link = next_message
    if req_body.parrent_message_id:
        req_msg = schemas.GetUserMsg(
            tg_id=req_body.tg_id,
            chapter_id=req_body.chapter_id,
            story_id=req_body.story_id,
            msg_id=req_body.parrent_message_id,
        )
        parrent_msg = get_check_user(db, req_msg)
        parrent_msg.link = new_msg
        db.add(parrent_msg)
    if req_body.is_start_msg:
        new_msg.is_start_chapter = True
        old_start_msg = db.query(models.Message).filter_by(
            chapter_id=req_body.chapter_id,
            is_start_chapter=True,
        ).first()
        if old_start_msg:
            old_start_msg.is_start_chapter = False

    db.add(new_msg)
    db.commit()
    db.refresh(new_msg)
    return new_msg


def get(db: Session, req_body: schemas.GetMsg) -> models.Message:
    """Return message by id."""
    msg = db.query(models.Message).filter_by(
        id=req_body.msg_id,
    ).first()
    if msg:
        return msg

    err_msg = 'There is not message id - {msg_id}'.format(
        msg_id=req_body.msg_id,
    )
    logger.error(err_msg)
    raise ValueError(err_msg)


def get_start_for_chapter(db: Session, req_body: schemas.GetMsgStartForChapter) -> Optional[models.Message]:
    """Return start message for chapter."""
    return db.query(models.Message).filter_by(
        chapter_id=req_body.chapter_id,
        is_start_chapter=True,
    ).first()


def get_check_user(
    db: Session,
    req_body: schemas.GetUserMsg,
) -> models.Message:
    """Return message by id."""
    msg = db.query(models.Message).filter_by(id=req_body.msg_id).first()
    if msg and msg.chapter.story.author.telegram_id == req_body.tg_id:
        return msg
    if not msg:
        err_msg = 'There is not message id - {msg_id}'.format(
            msg_id=req_body.msg_id,
        )
    elif msg.chapter.story.author.telegram_id != req_body.tg_id:
        err_msg = 'For message id - {msg_id} access denied'.format(
            msg_id=req_body.msg_id,
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
    msg.content_type = req_body.content_type
    if req_body.message:
        msg.message = req_body.message
    if req_body.next_message_id:
        req_msg = schemas.GetUserMsg(
            msg_id=req_body.next_message_id,
            tg_id=req_body.tg_id,
        )
        next_message = get_check_user(db, req_msg)
        msg.link = next_message
    if req_body.is_start_msg:
        msg.is_start_chapter = True
        old_start_msg = db.query(models.Message).filter_by(
            chapter_id=req_body.chapter_id,
            is_start_chapter=True,
        ).first()
        if old_start_msg:
            old_start_msg.is_start_chapter = False
    db.commit()
    db.refresh(msg)
    return msg
