"""Data base app."""
import logging

from data_base import schemas
from data_base.db_utils import get_db
from data_base.services import story, message, media
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
from data_base import schemas

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get('/{story_uid}')
def story_get(story_uid: str, db: Session = Depends(get_db)):
    """Return first story message."""
    try:
        first_message = story.get_first_msg(db, story_uid)
    except ValueError as val_err:
        return {'error': val_err.args}
    return first_message.to_engine_dict()


@router.get('/{story_uid}/msg/{msg_id}')
def msg_get(story_uid: str, msg_id: str, db: Session = Depends(get_db)):
    """Return message."""
    try:
        _message = message.get_open_msg(db, story_uid, int(msg_id))
    except ValueError as val_err:
        return {'error': val_err.args}
    return _message.to_engine_dict()


@router.get('/{story_uid}/start_chapter_msg/{chapter_id}')
def start_chapter_msg(story_uid: str, chapter_id: str, db: Session = Depends(get_db)):
    """Return message."""
    try:
        _message = message.get_open_start_for_chapter(db, story_uid, int(chapter_id))
    except ValueError as val_err:
        return {'error': val_err.args}
    return _message.to_engine_dict()


@router.get('/{story_uid}/wait_reactions/{wr_uid}')
def wait_reactions_get(story_uid: str, wr_uid: str, db: Session = Depends(get_db)):
    """Return wait reactions."""
    try:
        reactions = story.get_reactions_by_uid(db, story_uid, wr_uid)
    except ValueError as val_err:
        return {'error': val_err.args}
    return reactions.full_to_dict()


@router.get('/{story_uid}/media/{media_uid}')
def media_get(story_uid: str, media_uid: str, db: Session = Depends(get_db)):
    """Return media."""
    try:
        msg_media = media.get_by_uid(db, story_uid, media_uid)
    except ValueError as val_err:
        return {'error': val_err.args}
    return Response(content=msg_media.file_data, media_type=msg_media.content_type)