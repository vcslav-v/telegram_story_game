"""Data base app."""
import logging

from data_base.db_utils import get_db
from data_base.services import story
from data_base.schemas import MakeStory, GetStory, RenameStory
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post('/make')
def make(req_body: MakeStory, db: Session = Depends(get_db)):
    """Make and return new story."""
    try:
        new_story = story.make(db, req_body)
    except ValueError:
        return {'error': 'Story exist already.'}
    return new_story.to_dict()


@router.post('/get')
def get(req_body: GetStory, db: Session = Depends(get_db)):
    """Get exist story."""
    try:
        resp_story = story.get(db, req_body)
    except ValueError:
        return {'error': 'Story is not exist.'}
    return resp_story.to_dict()


@router.post('/rm')
def rm(req_body: GetStory, db: Session = Depends(get_db)):
    """Delete story."""
    try:
        status = story.rm(db, req_body)
    except ValueError:
        return {'error': 'Story is not exist.'}
    return status


@router.post('/rename')
def rename(req_body: RenameStory, db: Session = Depends(get_db)):
    """Rename story."""
    try:
        resp_story = story.rename(db, req_body)
    except ValueError:
        return {'error': 'Story is not exist.'}
    return resp_story
