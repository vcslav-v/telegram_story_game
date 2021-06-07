"""Data base app."""
import logging

from data_base import models, schemas
from data_base.services import message
from sqlalchemy.orm import Session
from fastapi import UploadFile

logger = logging.getLogger(__name__)


def make(
    db: Session,
    message_id: int,
    tg_id: int,
    file_data: UploadFile,
):
    msg_req_body = schemas.GetUserMsg(
        msg_id=message_id,
        tg_id=tg_id,
    )
    usr_message = message.get_check_user(db, msg_req_body)
    if usr_message.media:
        media = usr_message.media
    else:
        media = models.Media(
            parrent_message=usr_message,
        )
        db.add(media)
    media.content_type = file_data.content_type
    media.file_data = file_data.file.read()
    media.make_uid()
    db.commit()


def get(
    db: Session,
    id_media: int
):
    msg_media = db.query(models.Media).filter_by(id=id_media).first()
    if msg_media:
        return msg_media
    err_msg = f'There is not media id - {id_media}'
    logger.error(err_msg)
    raise ValueError(err_msg)


def get_by_uid(
    db: Session,
    story_uid: str,
    uid_media: str,
):
    story = db.query(models.Story).filter_by(uid=story_uid).first()
    msg_media = db.query(models.Media).filter_by(uid=uid_media).first()
    if msg_media and msg_media.parrent_message.chapter.story == story:
        return msg_media
    err_msg = f'There is not media id - {uid_media}'
    logger.error(err_msg)
    raise ValueError(err_msg)
