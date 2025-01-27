import aiohttp
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
from .types import (
    DiscordMessage,
    ChannelCreate,
    MessageEmbed,
    DiscordChannelType
)
from django.conf import settings

class DiscordService:
    def __init__(self):
        self.api_version = "10"
        self.base_url = f"https://discord.com/api/v{self.api_version}"
        self.bot_token = settings.DISCORD_BOT_TOKEN
        self.headers = {
            "Authorization": f"Bot {self.bot_token}",
            "Content-Type": "application/json"
        }

    async def send_message(
        self,
        channel_id: str,
        message: DiscordMessage
    ) -> Dict[str, Any]:
        """Send a message to Discord channel"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = message.dict(exclude_none=True)
                async with session.post(
                    f"{self.base_url}/channels/{channel_id}/messages",
                    headers=self.headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        raise Exception(f"Discord API Error: {error_data}")
                        
                    result = await response.json()
                    return {
                        "message_id": result["id"],
                        "channel_id": result["channel_id"],
                        "content": result.get("content"),
                        "timestamp": result["timestamp"]
                    }
                    
        except Exception as e:
            raise Exception(f"Failed to send message: {str(e)}")

    async def create_channel(
        self,
        guild_id: str,
        channel: ChannelCreate
    ) -> Dict[str, Any]:
        """Create a Discord channel"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = channel.dict(exclude_none=True)
                async with session.post(
                    f"{self.base_url}/guilds/{guild_id}/channels",
                    headers=self.headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        raise Exception(f"Discord API Error: {error_data}")
                        
                    result = await response.json()
                    return {
                        "channel_id": result["id"],
                        "name": result["name"],
                        "type": result["type"],
                        "position": result["position"]
                    }
                    
        except Exception as e:
            raise Exception(f"Failed to create channel: {str(e)}")

    async def edit_message(
        self,
        channel_id: str,
        message_id: str,
        message: DiscordMessage
    ) -> Dict[str, Any]:
        """Edit a Discord message"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = message.dict(exclude_none=True)
                async with session.patch(
                    f"{self.base_url}/channels/{channel_id}/messages/{message_id}",
                    headers=self.headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        raise Exception(f"Discord API Error: {error_data}")
                        
                    result = await response.json()
                    return {
                        "message_id": result["id"],
                        "content": result.get("content"),
                        "edited_timestamp": result["edited_timestamp"]
                    }
                    
        except Exception as e:
            raise Exception(f"Failed to edit message: {str(e)}")

    async def add_reaction(
        self,
        channel_id: str,
        message_id: str,
        emoji: str
    ) -> bool:
        """Add a reaction to a message"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.put(
                    f"{self.base_url}/channels/{channel_id}/messages/{message_id}/reactions/{emoji}/@me",
                    headers=self.headers
                ) as response:
                    return response.status == 204
                    
        except Exception as e:
            raise Exception(f"Failed to add reaction: {str(e)}")

    async def get_channel_messages(
        self,
        channel_id: str,
        limit: int = 50,
        before: Optional[str] = None,
        after: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get messages from a channel"""
        try:
            params = {"limit": min(limit, 100)}
            if before:
                params["before"] = before
            if after:
                params["after"] = after

            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/channels/{channel_id}/messages",
                    headers=self.headers,
                    params=params
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        raise Exception(f"Discord API Error: {error_data}")
                        
                    messages = await response.json()
                    return [
                        {
                            "id": msg["id"],
                            "content": msg.get("content"),
                            "author": msg["author"],
                            "timestamp": msg["timestamp"],
                            "embeds": msg.get("embeds", [])
                        }
                        for msg in messages
                    ]
                    
        except Exception as e:
            raise Exception(f"Failed to get messages: {str(e)}")

    async def create_thread(
        self,
        channel_id: str,
        name: str,
        message_id: Optional[str] = None,
        auto_archive_duration: int = 1440
    ) -> Dict[str, Any]:
        """Create a thread in a channel"""
        try:
            endpoint = f"{self.base_url}/channels/{channel_id}"
            if message_id:
                endpoint += f"/messages/{message_id}/threads"
            else:
                endpoint += "/threads"

            payload = {
                "name": name,
                "auto_archive_duration": auto_archive_duration
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint,
                    headers=self.headers,
                    json=payload
                ) as response:
                    if response.status not in [200, 201]:
                        error_data = await response.json()
                        raise Exception(f"Discord API Error: {error_data}")
                        
                    result = await response.json()
                    return {
                        "thread_id": result["id"],
                        "name": result["name"],
                        "parent_id": result["parent_id"],
                        "owner_id": result["owner_id"]
                    }
                    
        except Exception as e:
            raise Exception(f"Failed to create thread: {str(e)}")

    async def get_guild_channels(
        self,
        guild_id: str
    ) -> List[Dict[str, Any]]:
        """Get all channels in a guild"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/guilds/{guild_id}/channels",
                    headers=self.headers
                ) as response:
                    if response.status != 200:
                        error_data = await response.json()
                        raise Exception(f"Discord API Error: {error_data}")
                        
                    channels = await response.json()
                    return [
                        {
                            "id": channel["id"],
                            "name": channel["name"],
                            "type": channel["type"],
                            "parent_id": channel.get("parent_id"),
                            "position": channel["position"]
                        }
                        for channel in channels
                    ]
                    
        except Exception as e:
            raise Exception(f"Failed to get channels: {str(e)}")