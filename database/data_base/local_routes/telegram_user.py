"""Data base app."""
import logging

from data_base.db_utils import get_db
from data_base import schemas
from data_base.services import telegram_user
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post('/get')
def get_or_make_if_exist(
    req_body: schemas.TgUser,
    db: Session = Depends(get_db),
):
    """Return user if one exist or add new user to db."""
    return telegram_user.get_or_make_if_new(db, req_body).to_dict()
