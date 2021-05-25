"""Data base app."""
import logging

from data_base.db_utils import get_db
from data_base.schemas import (GetChapter, GetUserChapter, MakeChapter,
                               RenameChapter, ReplaceChapter, GetChapterMap)
from data_base.services import chapter
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post('/make')
def make(req_body: MakeChapter, db: Session = Depends(get_db)):
    """Make and return new chapter."""
    try:
        new_chapter = chapter.make(db, req_body)
    except ValueError as val_err:
        return {'error': val_err.args}
    return new_chapter.to_dict()


@router.post('/get')
def get(req_body: GetChapter, db: Session = Depends(get_db)):
    """Get and return new story."""
    try:
        story_chapter = chapter.get(db, req_body)
    except ValueError as val_err:
        return {'error': val_err.args}
    return story_chapter.to_dict()


@router.post('/rename')
def rename(req_body: RenameChapter, db: Session = Depends(get_db)):
    """Get and return new story."""
    try:
        story_chapter = chapter.rename(db, req_body)
    except ValueError as val_err:
        return {'error': val_err.args}
    return story_chapter.to_dict()


@router.post('/replace')
def replace(req_body: ReplaceChapter, db: Session = Depends(get_db)):
    """Get and return new story."""
    try:
        story_chapter = chapter.replace(db, req_body)
    except ValueError as val_err:
        return {'error': val_err.args}
    return story_chapter.to_dict()


@router.post('/rm')
def rm(req_body: GetUserChapter, db: Session = Depends(get_db)):
    """Get and return new story."""
    try:
        status = chapter.rm(db, req_body)
    except ValueError as val_err:
        return {'error': val_err.args}
    return status


@router.post('/get_chapter_map')
def get_chapter_map(req_body: GetChapterMap, db: Session = Depends(get_db)):
    """Get and return new story."""
    try:
        _chapter = chapter.get_chapter_by_uid(db, req_body)
    except ValueError as val_err:
        return {'error': val_err.args}
    return _chapter.messages_map_to_dict()
