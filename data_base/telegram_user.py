"""Data base app."""
import logging

from data_base import db, models

logger = logging.getLogger(__name__)


def get_or_make_if_new(telegram_id: int) -> dict:
    """Return user if one exist or add new user to db."""
    session = db.Session()
    user = session.query(models.TelegramUser).filter_by(
        telegram_id=telegram_id,
    ).first()
    if user:
        repr_user = user.to_dict()
        session.close()
        return repr_user

    user = models.TelegramUser(telegram_id=telegram_id)

    session.add(user)
    session.commit()
    repr_user = user.to_dict()
    session.close()
    return repr_user


def get_model(session, user_id: int) -> models.TelegramUser:
    """Return TelegramUser db model."""
    user = session.query(models.TelegramUser).filter_by(
        id=user_id,
    ).first()
    if not user:
        session.close()
        err_msg = 'Cant make story user id-{user_id} is not exist.'.format(
            user_id=user_id,
        )
        logger.error(err_msg)
        raise ValueError(err_msg)
    return user
