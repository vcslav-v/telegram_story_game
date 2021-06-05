"""Data base app."""
import logging

from data_base.db_utils import get_db
from data_base.services import media
from fastapi import APIRouter, Depends, Form, File, UploadFile, Response
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post('/make')
def make(
    message_id: int = Form(...),
    tg_id: int = Form(...),
    file_data: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Make media."""
    try:
        media.make(db, message_id, tg_id, file_data)
    except ValueError as val_err:
        return {'error': val_err.args}
    return {'status': 'ok'}


@router.get('/get/{id_media}')
def get(
    id_media: str,
    db: Session = Depends(get_db),
):
    """Get media."""
    try:
        msg_media = media.get(db, int(id_media))
    except ValueError as val_err:
        return {'error': val_err.args}
    return Response(content=msg_media.file_data, media_type=msg_media.content_type)
