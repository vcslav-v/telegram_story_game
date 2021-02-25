import logging

from data_base import models, schemas
from data_base.services import message
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def add(
    db: Session,
    req_body: schemas.AddButton,
) -> models.Message:
    """Make and add button to message."""
    msg = message.get_check_user(db, req_body)
    new_button = models.Button(
        text=req_body.text,
        parrent_message=msg,
    )
    db.add(new_button)
    db.commit()
    db.refresh(msg)
    return msg


def _get(
    db: Session,
    req_body: schemas.GetMsgButton,
) -> models.Button:
    """Get button."""
    msg = message.get_check_user(db, req_body)
    btn = db.query(models.Button).filter_by(
        id=req_body.button_id,
        parrent_message=msg,
    ).first()
    if btn:
        return btn

    err_msg = 'There is not button id - {button_id} for story {msg_id}'.format(
        button_id=req_body.button_id,
        msg_id=req_body.msg_id,
    )
    logger.error(err_msg)
    raise ValueError(err_msg)


def rm(
    db: Session,
    req_body: schemas.GetMsgButton,
) -> models.Message:
    """Remove button."""
    msg = message.get_check_user(db, req_body)
    btn = _get(db, req_body)
    db.delete(btn)
    db.commit()
    db.refresh(msg)
    return msg


def edit(
    db: Session,
    req_body: schemas.EditButton,
) -> models.Message:
    """Edit button."""
    msg = message.get_check_user(db, req_body)
    btn = _get(db, req_body)
    if req_body.text:
        btn.text = req_body.text
    if req_body.link_to_msg_id:
        req_msg = schemas.GetUserMsg(
            tg_id=req_body.tg_id,
            story_id=req_body.story_id,
            msg_id=req_body.link_to_msg_id,
        )
        req_msg.msg_id = req_body.link_to_msg_id
        msg = message.get_check_user(db, req_msg)
        btn.next_message = msg
    db.commit()
    db.refresh(msg)
    return msg
