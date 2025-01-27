from fastapi import APIRouter, HTTPException, Depends, Query
from typing import List, Optional
from ....services.integrations.discord.discord_service import DiscordService
from ....services.integrations.discord.types import (
    DiscordMessage,
    ChannelCreate,
    MessageEmbed,
    DiscordChannelType
)
from ....core.auth import get_current_user

router = APIRouter(prefix="/discord", tags=["Discord"])
discord_service = DiscordService()

@router.post("/channels/{channel_id}/messages")
async def send_message(
    channel_id: str,
    message: DiscordMessage,
    current_user: dict = Depends(get_current_user)
):
    """Send a Discord message"""
    try:
        result = await discord_service.send_message(
            channel_id=channel_id,
            message=message
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/guilds/{guild_id}/channels")
async def create_channel(
    guild_id: str,
    channel: ChannelCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a Discord channel"""
    try:
        result = await discord_service.create_channel(
            guild_id=guild_id,
            channel=channel
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/channels/{channel_id}/messages/{message_id}")
async def edit_message(
    channel_id: str,
    message_id: str,
    message: DiscordMessage,
    current_user: dict = Depends(get_current_user)
):
    """Edit a Discord message"""
    try:
        result = await discord_service.edit_message(
            channel_id=channel_id,
            message_id=message_id,
            message=message
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/channels/{channel_id}/messages/{message_id}/reactions/{emoji}")
async def add_reaction(
    channel_id: str,
    message_id: str,
    emoji: str,
    current_user: dict = Depends(get_current_user)
):
    """Add a reaction to a message"""
    try:
        success = await discord_service.add_reaction(
            channel_id=channel_id,
            message_id=message_id,
            emoji=emoji
        )
        return {"success": success}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/channels/{channel_id}/messages")
async def get_messages(
    channel_id: str,
    limit: int = Query(default=50, le=100),
    before: Optional[str] = None,
    after: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get channel messages"""
    try:
        messages = await discord_service.get_channel_messages(
            channel_id=channel_id,
            limit=limit,
            before=before,
            after=after
        )
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/channels/{channel_id}/threads")
async def create_thread(
    channel_id: str,
    name: str,
    message_id: Optional[str] = None,
    auto_archive_duration: int = Query(default=1440, le=10080),
    current_user: dict = Depends(get_current_user)
):
    """Create a thread"""
    try:
        result = await discord_service.create_thread(
            channel_id=channel_id,
            name=name,
            message_id=message_id,
            auto_archive_duration=auto_archive_duration
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/guilds/{guild_id}/channels")
async def get_guild_channels(
    guild_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all channels in a guild"""
    try:
        channels = await discord_service.get_guild_channels(guild_id)
        return channels
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))