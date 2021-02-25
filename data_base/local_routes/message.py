"""Data base app."""
import logging

from data_base.db_utils import get_db
from data_base.schemas import MakeMsg, GetMsg, GetUserMsg
from data_base.services import message
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post('/make')
def make(req_body: MakeMsg, db: Session = Depends(get_db)):
    """Make and return new message."""
    try:
        new_msg = message.make(db, req_body)
    except ValueError:
        return {'error': 'Msg exist already.'}
    return new_msg.to_dict()


@router.post('/get')
def get(req_body: GetMsg, db: Session = Depends(get_db)):
    """Make and return new message."""
    try:
        new_msg = message.get(db, req_body)
    except ValueError:
        return {'error': 'Msg exist already.'}
    return new_msg.to_dict()


@router.post('/rm')
def rm(req_body: GetUserMsg, db: Session = Depends(get_db)):
    """Make and return new message."""
    try:
        status = message.rm(db, req_body)
    except ValueError:
        return {'error': 'Msg exist already.'}
    return status
