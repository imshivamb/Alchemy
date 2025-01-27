from enum import Enum
from pydantic import BaseModel
from typing import Optional, List, Dict, Any, Union

class DiscordMessageType(str, Enum):
    DEFAULT = "default"
    REPLY = "reply"
    EMBED = "embed"

class DiscordChannelType(str, Enum):
    TEXT = "text"
    VOICE = "voice"
    CATEGORY = "category"
    ANNOUNCEMENT = "announcement"
    FORUM = "forum"

class EmbedField(BaseModel):
    name: str
    value: str
    inline: bool = False

class EmbedFooter(BaseModel):
    text: str
    icon_url: Optional[str] = None

class MessageEmbed(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    color: Optional[int] = None
    fields: Optional[List[EmbedField]] = None
    footer: Optional[EmbedFooter] = None
    timestamp: Optional[str] = None

class DiscordMessage(BaseModel):
    content: Optional[str] = None
    embed: Optional[MessageEmbed] = None
    tts: bool = False
    message_reference: Optional[Dict[str, str]] = None  # For replies

class ChannelCreate(BaseModel):
    name: str
    type: DiscordChannelType
    topic: Optional[str] = None
    parent_id: Optional[str] = None  # Category ID
    nsfw: bool = False