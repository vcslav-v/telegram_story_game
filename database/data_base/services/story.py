"""Data base app."""
import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from fastapi import UploadFile
import csv
from typing import List

from data_base.services import telegram_user
from data_base import models, schemas

logger = logging.getLogger(__name__)


def make(
    db: Session,
    req_body: schemas.MakeStory,
) -> models.Story:
    """Make and return new story."""
    logger.info(
        'make a story - user_id = {tg_id}, str_name = {str_name}'.format(
            tg_id=req_body.tg_id,
            str_name=req_body.story_name,
        ),
    )
    user = telegram_user.get_or_make_if_new(db, req_body)

    new_story = models.Story(name=req_body.story_name, author=user)

    db.add(new_story)
    try:
        db.commit()
    except IntegrityError:
        err_msg = (
            'Cant make new story because story exist already. '
            'make a story - tg_id = {tg_id}, str_name = {str_name}'
        ).format(
            tg_id=req_body.tg_id,
            str_name=req_body.story_name,
        )
        logger.error(err_msg)
        raise ValueError(err_msg)
    db.refresh(new_story)
    return new_story


def get(
    db: Session,
    req_body: schemas.GetStory,
) -> models.Story:
    """Return story by name."""
    story = db.query(models.Story).filter_by(
        id=req_body.story_id,
    ).first()
    if story:
        return story
    err_msg = 'Story {story_id} is not exist'.format(
        story_id=req_body.story_id,
    )
    logger.error(err_msg)
    raise ValueError(err_msg)


def get_check_author(
    db: Session,
    req_body: schemas.GetUserStory,
) -> models.Story:
    """Return story by id."""
    story = db.query(models.Story).filter_by(
        id=req_body.story_id,
    ).first()
    if story and story.author.telegram_id == req_body.tg_id:
        return story
    err_msg = 'Story {story_id} is not exist or access denied'.format(
        story_id=req_body.story_id,
    )
    logger.error(err_msg)
    raise ValueError(err_msg)


def rm(
    db: Session,
    req_body: schemas.GetUserStory,
) -> dict:
    """Delete story with chapter and mesages."""
    user_story = get_check_author(db, req_body)
    db.delete(user_story)
    db.commit()
    return {'result': 'ok'}


def rename(
    db: Session,
    req_body: schemas.RenameStory,
) -> models.Story:
    """Rename story."""
    user_story = get_check_author(db, req_body)
    user_story.name = req_body.new_name
    db.commit()
    db.refresh(user_story)
    return user_story


def edit(
    db: Session,
    req_body: schemas.EditStory,
) -> models.Story:
    """Edit story."""
    user_story = get_check_author(db, req_body)
    if req_body.base_timeout:
        user_story.base_timeout = req_body.base_timeout
    if req_body.k_timeout:
        user_story.k_timeout = req_body.k_timeout
    db.commit()
    db.refresh(user_story)
    return user_story


def set_reactions(
    db: Session,
    tg_id: int,
    story_id: int,
    file_data: UploadFile,
) -> models.Story:
    reader = csv.reader(file_data.file.read().decode('utf-8').splitlines())

    reactions: dict = {}
    headers = []
    for i, row in enumerate(reader):
        if i > 9:
            break
        if i == 0:
            headers.extend(row)
            for header in headers:
                reactions[header] = []
        else:
            for j, header in enumerate(headers):
                reactions[header].append(row[j])

    req_body = schemas.GetUserStory(
        story_id=story_id,
        tg_id=tg_id,
    )
    usr_story = get_check_author(db, req_body)
    for wait_reaction in usr_story.wait_reactions:
        db.delete(wait_reaction)
    for reaction, responses in reactions.items():
        wait_reactinon = models.WaitReaction(
            name=reaction,
            story=usr_story,
        )
        db.add(wait_reactinon)
        for response in responses:
            if response:
                db.add(models.Reactions(
                    message=response,
                    wait_reaction=wait_reactinon,
                ))
    db.commit()
    db.refresh(usr_story)
    return usr_story


def get_reactions(
    db: Session,
    req_body: schemas.GetUserStory,
) -> List[models.WaitReaction]:
    usr_story = get_check_author(db, req_body)
    return usr_story.wait_reactions
