"""Pydantic's models."""

from typing import Optional

from pydantic import BaseModel


class TgUser(BaseModel):
    """User model."""

    tg_id: int


class MakeStory(TgUser):
    """Make story model."""

    story_name: str


class GetStory(TgUser):
    """Get story model."""

    story_id: int


class RenameStory(GetStory):
    """Rename story model."""

    new_name: str


class MakeChapter(GetStory):
    """Chapter model."""

    chapter_name: str
    chapter_num: Optional[int]


class GetChapter(GetStory):
    """Chapter model."""

    chapter_id: int


class RenameChapter(GetChapter):
    """Chapter model."""

    new_name: str


class ReplaceChapter(GetChapter):
    """Chapter model."""

    new_num: int


class GetMsg(GetStory):
    """Message model."""

    msg_id: int


class MakeMsg(GetStory):
    """Message model."""

    message: Optional[str]
    next_message_id: Optional[int]
