"""Data base app."""
import logging

from data_base import schemas
from data_base.db_utils import get_db
from data_base.services import message
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from data_base import schemas

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post('/get')
def get(req_body: schemas.GetMsg, db: Session = Depends(get_db)):
    """Make and return new message."""
    try:
        new_msg = message.get(db, req_body)
    except ValueError as val_err:
        return {'error': val_err.args}
    return new_msg.to_dict()
