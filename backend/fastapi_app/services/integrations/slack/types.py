from enum import Enum
from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any, Union

class SlackActionType(str, Enum):
    SEND_MESSAGE = "send_message"
    UPDATE_MESSAGE = "update_message"
    DELETE_MESSAGE = "delete_message"
    CREATE_CHANNEL = "create_channel"
    INVITE_USER = "invite_user"
    UPLOAD_FILE = "upload_file"

class MessageBlock(BaseModel):
    type: str
    text: Optional[Dict[str, str]] = None
    elements: Optional[List[Dict[str, Any]]] = None
    accessory: Optional[Dict[str, Any]] = None

class SlackMessage(BaseModel):
    channel: str
    text: Optional[str] = None
    blocks: Optional[List[MessageBlock]] = None
    thread_ts: Optional[str] = None
    reply_broadcast: Optional[bool] = False
    unfurl_links: Optional[bool] = True
    unfurl_media: Optional[bool] = True
    mrkdwn: Optional[bool] = True

class FileUpload(BaseModel):
    channels: List[str]
    content: Optional[str] = None
    file_path: Optional[str] = None
    filename: str
    filetype: Optional[str] = None
    initial_comment: Optional[str] = None
    thread_ts: Optional[str] = None

class ChannelCreate(BaseModel):
    name: str
    is_private: bool = False
    team_id: Optional[str] = None

class UserInvite(BaseModel):
    channel: str
    users: List[str]

class SlackResponse(BaseModel):
    ok: bool
    error: Optional[str] = None
    warning: Optional[str] = None
    response_metadata: Optional[Dict[str, Any]] = None 