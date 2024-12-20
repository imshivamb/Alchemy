import aiohttp
from typing import Dict, Any, List, Optional
from datetime import datetime
from ...oauth.token_manager import TokenManager
from fastapi_app.types.oauth_types import OAuthProvider
from .types import (
    SlackMessage,
    FileUpload,
    ChannelCreate,
    MessageBlock
)

class SlackService:
    def __init__(self):
        self.token_manager = TokenManager()
        self.base_url = "https://slack.com/api"

    async def _get_headers(self, user_id: str) -> Dict[str, str]:
        """Get authorization headers"""
        token = await self.token_manager.get_valid_token(
            user_id,
            OAuthProvider.SLACK
        )
        if not token:
            raise ValueError("No valid Slack token found")
            
        return {
            "Authorization": f"Bearer {token.access_token}",
            "Content-Type": "application/json"
        }

    async def send_message(
        self,
        user_id: str,
        message: SlackMessage
    ) -> Dict[str, Any]:
        """Send a message to Slack"""
        try:
            headers = await self._get_headers(user_id)
            
            async with aiohttp.ClientSession() as session:
                payload = message.dict(exclude_none=True)
                async with session.post(
                    f"{self.base_url}/chat.postMessage",
                    headers=headers,
                    json=payload
                ) as response:
                    result = await response.json()
                    
                    if not result["ok"]:
                        raise Exception(result["error"])
                        
                    return {
                        "message_id": result["ts"],
                        "channel": result["channel"],
                        "message": result["message"]
                    }
                    
        except Exception as e:
            raise Exception(f"Failed to send message: {str(e)}")

    async def create_channel(
        self,
        user_id: str,
        channel: ChannelCreate
    ) -> Dict[str, Any]:
        """Create a Slack channel"""
        try:
            headers = await self._get_headers(user_id)
            
            endpoint = "conversations.create"
            payload = {
                "name": channel.name,
                "is_private": channel.is_private
            }
            if channel.team_id:
                payload["team_id"] = channel.team_id
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/{endpoint}",
                    headers=headers,
                    json=payload
                ) as response:
                    result = await response.json()
                    
                    if not result["ok"]:
                        raise Exception(result["error"])
                        
                    return {
                        "channel_id": result["channel"]["id"],
                        "name": result["channel"]["name"],
                        "is_private": result["channel"]["is_private"]
                    }
                    
        except Exception as e:
            raise Exception(f"Failed to create channel: {str(e)}")

    async def upload_file(
        self,
        user_id: str,
        file: FileUpload
    ) -> Dict[str, Any]:
        """Upload a file to Slack"""
        try:
            headers = await self._get_headers(user_id)
            headers.pop("Content-Type", None)  # Let aiohttp set correct content type
            
            data = {
                "channels": ",".join(file.channels)
            }
            
            if file.title:
                data["title"] = file.title
            if file.initial_comment:
                data["initial_comment"] = file.initial_comment
            if file.thread_ts:
                data["thread_ts"] = file.thread_ts

            files = {}
            if file.content:
                files['file'] = ('file.txt', file.content)
            elif file.file_path:
                with open(file.file_path, 'rb') as f:
                    files['file'] = (file.file_path.split('/')[-1], f.read())

            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/files.upload",
                    headers=headers,
                    data=data,
                    files=files
                ) as response:
                    result = await response.json()
                    
                    if not result["ok"]:
                        raise Exception(result["error"])
                        
                    return {
                        "file_id": result["file"]["id"],
                        "url": result["file"]["url"],
                        "permalink": result["file"]["permalink"]
                    }
                    
        except Exception as e:
            raise Exception(f"Failed to upload file: {str(e)}")

    async def update_message(
        self,
        user_id: str,
        channel: str,
        message_ts: str,
        text: Optional[str] = None,
        blocks: Optional[List[MessageBlock]] = None
    ) -> Dict[str, Any]:
        """Update a Slack message"""
        try:
            headers = await self._get_headers(user_id)
            
            payload = {
                "channel": channel,
                "ts": message_ts
            }
            
            if text:
                payload["text"] = text
            if blocks:
                payload["blocks"] = [block.dict() for block in blocks]
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat.update",
                    headers=headers,
                    json=payload
                ) as response:
                    result = await response.json()
                    
                    if not result["ok"]:
                        raise Exception(result["error"])
                        
                    return {
                        "message_ts": result["ts"],
                        "channel": result["channel"],
                        "text": result.get("text"),
                        "blocks": result.get("blocks")
                    }
                    
        except Exception as e:
            raise Exception(f"Failed to update message: {str(e)}")

    async def add_reaction(
        self,
        user_id: str,
        channel: str,
        timestamp: str,
        emoji: str
    ) -> Dict[str, Any]:
        """Add a reaction to a message"""
        try:
            headers = await self._get_headers(user_id)
            
            payload = {
                "channel": channel,
                "timestamp": timestamp,
                "name": emoji.strip(':')  # Remove colons if present
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/reactions.add",
                    headers=headers,
                    json=payload
                ) as response:
                    result = await response.json()
                    
                    if not result["ok"]:
                        raise Exception(result["error"])
                        
                    return {"success": True}
                    
        except Exception as e:
            raise Exception(f"Failed to add reaction: {str(e)}")

    async def get_channel_info(
        self,
        user_id: str,
        channel_id: str
    ) -> Dict[str, Any]:
        """Get channel information"""
        try:
            headers = await self._get_headers(user_id)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/conversations.info",
                    headers=headers,
                    params={"channel": channel_id}
                ) as response:
                    result = await response.json()
                    
                    if not result["ok"]:
                        raise Exception(result["error"])
                        
                    return result["channel"]
                    
        except Exception as e:
            raise Exception(f"Failed to get channel info: {str(e)}")

    async def invite_to_channel(
        self,
        user_id: str,
        channel_id: str,
        user_ids: List[str]
    ) -> Dict[str, Any]:
        """Invite users to a channel"""
        try:
            headers = await self._get_headers(user_id)
            
            payload = {
                "channel": channel_id,
                "users": ",".join(user_ids)
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/conversations.invite",
                    headers=headers,
                    json=payload
                ) as response:
                    result = await response.json()
                    
                    if not result["ok"]:
                        raise Exception(result["error"])
                        
                    return {
                        "channel": result["channel"],
                        "invited_users": user_ids
                    }
                    
        except Exception as e:
            raise Exception(f"Failed to invite users: {str(e)}")