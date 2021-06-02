"""Data base app."""
import logging

from data_base.db_utils import get_db
from data_base.schemas import (EditStory, GetStory, GetUserStory,
                               MakeStory, RenameStory)
from data_base.services import story
from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post('/make')
def make(req_body: MakeStory, db: Session = Depends(get_db)):
    """Make and return new story."""
    try:
        new_story = story.make(db, req_body)
    except ValueError as val_err:
        return {'error': val_err.args}
    return new_story.to_dict()


@router.post('/get')
def get(req_body: GetStory, db: Session = Depends(get_db)):
    """Get exist story."""
    try:
        resp_story = story.get(db, req_body)
    except ValueError as val_err:
        return {'error': val_err.args}
    return resp_story.to_dict()


@router.post('/rm')
def rm(req_body: GetUserStory, db: Session = Depends(get_db)):
    """Delete story."""
    try:
        status = story.rm(db, req_body)
    except ValueError as val_err:
        return {'error': val_err.args}
    return status


@router.post('/rename')
def rename(req_body: RenameStory, db: Session = Depends(get_db)):
    """Rename story."""
    try:
        resp_story = story.rename(db, req_body)
    except ValueError as val_err:
        return {'error': val_err.args}
    return resp_story


@router.post('/edit')
def edit(req_body: EditStory, db: Session = Depends(get_db)):
    """Edit story."""
    try:
        resp_story = story.edit(db, req_body)
    except ValueError as val_err:
        return {'error': val_err.args}
    return resp_story


@router.post('/set-reactions')
def set_reactions(
    tg_id: int = Form(...),
    story_id: int = Form(...),
    file_data: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Set reactions."""
    try:
        usr_story = story.set_reactions(db, tg_id, story_id, file_data)
    except ValueError as val_err:
        return {'error': val_err.args}
    return usr_story.to_dict()


@router.post('/get-reactions')
def get_reactions(req_body: GetUserStory, db: Session = Depends(get_db)):
    try:
        reactions = story.get_reactions(db, req_body)
    except ValueError as val_err:
        return {'error': val_err.args}
    return {'reactions': [reaction.to_dict() for reaction in reactions]}


@router.post('/get-reactions-list')
def get_reactions_list(req_body: GetUserStory, db: Session = Depends(get_db)):
    try:
        reactions = story.get_reactions(db, req_body)
    except ValueError as val_err:
        return {'error': val_err.args}
    return {'reactions': [reaction.full_to_dict() for reaction in reactions]}
