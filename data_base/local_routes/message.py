"""Data base app."""
import logging

from data_base.db_utils import get_db
from data_base.schemas import MakeMsg, GetMsg, GetUserMsg, EditMsg, AddButton, GetMsgButton, EditButton
from data_base.services import message, button
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post('/make')
def make(req_body: MakeMsg, db: Session = Depends(get_db)):
    """Make and return new message."""
    try:
        new_msg = message.make(db, req_body)
    except Exception as e:
        print(e)
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


@router.post('/edit')
def edit(req_body: EditMsg, db: Session = Depends(get_db)):
    """Make and return new message."""
    try:
        status = message.edit(db, req_body)
    except ValueError:
        return {'error': 'Msg exist already.'}
    return status


@router.post('/add_button')
def add_button(req_body: AddButton, db: Session = Depends(get_db)):
    """Make and return new message."""
    try:
        msg = button.add(db, req_body)
    except ValueError:
        return {'error': 'Msg exist already.'}
    return msg.to_dict()


@router.post('/rm_button')
def rm_button(req_body: GetMsgButton, db: Session = Depends(get_db)):
    """Make and return new message."""
    try:
        msg = button.rm(db, req_body)
    except ValueError:
        return {'error': 'Msg exist already.'}
    return msg.to_dict()


@router.post('/edit_button')
def edit_button(req_body: EditButton, db: Session = Depends(get_db)):
    """Make and return new message."""
    try:
        msg = button.edit(db, req_body)
    except ValueError:
        return {'error': 'Msg exist already.'}
    return msg.to_dict()
