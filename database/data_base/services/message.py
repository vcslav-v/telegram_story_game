"""Data base app."""
import logging
from typing import Optional

from data_base import models, schemas
from data_base.services import chapter
from sqlalchemy.orm import Session
from loguru import logger


def make(
    db: Session,
    req_body: schemas.MakeMsg,
) -> models.Message:
    """Make new message."""
    user_chapter = chapter.get_check_user(db, req_body)
    new_msg = models.Message(
        chapter=user_chapter,
        content_type=req_body.content_type,
        timeout=user_chapter.story.base_timeout,
    )
    reaction = db.query(models.WaitReaction).filter_by(
        story_id=user_chapter.story_id,
        name='std',
    ).first()
    if reaction:
        new_msg.wait_reaction = reaction
    if req_body.message:
        new_msg.message = req_body.message

    if req_body.next_message_id:
        req_msg = schemas.GetUserMsg(
            tg_id=req_body.tg_id,
            story_id=req_body.story_id,
            msg_id=req_body.next_message_id,
        )
        next_message = get_check_user(db, req_msg)
        new_msg.link_id = next_message.id
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

    if req_body.parrent_message_id:
        req_msg = schemas.GetUserMsg(
            tg_id=req_body.tg_id,
            chapter_id=req_body.chapter_id,
            story_id=req_body.story_id,
            msg_id=req_body.parrent_message_id,
        )
        parrent_msg = get_check_user(db, req_msg)
        parrent_msg.link_id = new_msg.id
        db.add(parrent_msg)
    
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


def get_open_msg(db: Session, story_uid: str, msg_id: int):
    msg = db.query(models.Message).filter_by(
            id=msg_id,
    ).first()
    if msg and msg.chapter.story.uid == story_uid:
        return msg

    err_msg = 'There is not message id - {msg_id}'.format(
        msg_id=msg_id,
    )
    logger.error(err_msg)
    raise ValueError(err_msg)


def get_open_start_for_chapter(db: Session, story_uid: str, chapter_id: int):
    msg = db.query(models.Message).filter_by(
        chapter_id=chapter_id,
        is_start_chapter=True,
    ).first()
    if msg and msg.chapter.story.uid == story_uid:
        return msg

    err_msg = 'There is not message id - {msg_id}'.format(
        msg_id=msg_id,
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

@logger.catch
def edit(db: Session, req_body: schemas.EditMsg) -> models.Message:
    """Edit text message by id."""
    msg = get_check_user(db, req_body)
    if req_body.message:
        msg.message = req_body.message
    if req_body.content_type:
        msg.content_type = req_body.content_type
        if not req_body.message and req_body.content_type != 'text':
            msg.message = req_body.message
    if req_body.referal_block is not None:
        msg.referal_block = req_body.referal_block
    if req_body.next_message_id:
        req_msg = schemas.GetUserMsg(
            msg_id=req_body.next_message_id,
            tg_id=req_body.tg_id,
        )
        next_message = get_check_user(db, req_msg)
        msg.link_id = next_message.id
    if req_body.is_start_msg:
        msg.is_start_chapter = True
        old_start_msg = db.query(models.Message).filter_by(
            chapter_id=req_body.chapter_id,
            is_start_chapter=True,
        ).first()
        if old_start_msg:
            old_start_msg.is_start_chapter = False
    if req_body.timeout is not None:
        msg.timeout = req_body.timeout
    if req_body.reaction_id:
        reaction = db.query(models.WaitReaction).filter_by(id=req_body.reaction_id).first()
        if reaction and reaction.story.author.telegram_id == req_body.tg_id:
            msg.wait_reaction = reaction
    db.commit()
    db.refresh(msg)
    return msg
