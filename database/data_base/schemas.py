"""Pydantic's models."""

from typing import Optional

from pydantic import BaseModel


class TgUser(BaseModel):
    """User model."""

    tg_id: int


class MakeStory(TgUser):
    """Make story model."""

    story_name: str


class GetStory(BaseModel):
    """Get story model."""

    story_id: int


class GetUserStory(TgUser):
    """Get story model."""

    story_id: int


class RenameStory(GetUserStory):
    """Rename story model."""

    new_name: str


class EditStory(GetUserStory):
    """Edit story model."""

    base_timeout: Optional[int]
    k_timeout: Optional[int]

class MakeChapter(GetUserStory):
    """Chapter model."""

    chapter_name: str
    chapter_num: Optional[int]


class GetChapter(GetStory):
    """Chapter model."""

    chapter_id: int


class GetChapterMap(BaseModel):
    """Chapter map model."""

    chapter_hash: str


class GetUserChapter(TgUser, GetChapter):
    """Chapter model."""

    pass


class RenameChapter(GetUserChapter):
    """Chapter model."""

    new_name: str


class ReplaceChapter(GetUserChapter):
    """Chapter model."""

    new_num: int


class GetMsg(BaseModel):
    """Message model."""

    msg_id: int


class GetMsgStartForChapter(BaseModel):

    chapter_id: int


class GetUserMsg(TgUser, GetMsg):
    """Message model."""

    pass


class MakeMsg(GetUserChapter):
    """Message model."""

    content_type: str
    message: Optional[str]
    next_message_id: Optional[int]
    parrent_message_id: Optional[int]
    is_start_msg: Optional[bool]


class EditMsg(GetUserMsg):
    content_type: Optional[str]
    message: Optional[str]
    chapter_id: int
    next_message_id: Optional[int]
    is_start_msg: Optional[bool]
    timeout: Optional[int]
    reaction_id: Optional[int]
    referal_block: Optional[int]


class AddButton(GetUserMsg):
    """Button model."""

    text: str
    link_to_msg_id: Optional[int]


class GetMsgButton(GetUserMsg):
    """Button model."""

    button_id: int


class EditButton(GetMsgButton):
    """Button model."""

    text: Optional[str]
    link_to_msg_id: Optional[int]
    move: Optional[int]
