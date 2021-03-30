"""Data base app."""
import logging

from data_base import models, schemas
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


def get_or_make_if_new(
    db: Session,
    req_bory: schemas.TgUser,
) -> models.TelegramUser:
    """Return user if one exist or add new user to db."""
    user = db.query(models.TelegramUser).filter_by(
        telegram_id=req_bory.tg_id,
    ).first()
    if user:
        return user

    user = models.TelegramUser(telegram_id=req_bory.tg_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
