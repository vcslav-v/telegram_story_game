"""Data base app."""
import logging

from data_base import schemas
from data_base.db_utils import get_db
from data_base.services import story, message
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from data_base import schemas

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get('/{story_uid}')
def story_get(story_uid: str, db: Session = Depends(get_db)):
    """Return message."""
    try:
        first_message = story.get_first_msg(db, story_uid)
    except ValueError as val_err:
        return {'error': val_err.args}
    return first_message.to_engine_dict()


@router.get('/{story_uid}/{msg_id}')
def mmsg_get(story_uid: str, msg_id: str, db: Session = Depends(get_db)):
    """Return message."""
    try:
        _message = message.get_open_msg(db, story_uid, int(msg_id))
    except ValueError as val_err:
        return {'error': val_err.args}
    return _message.to_engine_dict()