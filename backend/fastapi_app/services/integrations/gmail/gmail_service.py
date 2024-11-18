import base64
from typing import List, Optional, Dict, Any
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email import encoders
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2.credentials import Credentials
from ...oauth.token_manager import TokenManager
from fastapi_app.types.oauth_types import OAuthProvider
from .types import (
    GmailActionType,
    EmailMessage,
    GmailFilter,
    EmailAttachment
)
from django.conf import settings


class GmailService:
    def __init__(self):
        self.token_manager = TokenManager()
        
    async def get_client(self, user_id: str):
        """Get Authenticated Gmail Client"""
        token = await self.token_manager.get_valid_token(user_id, OAuthProvider.GOOGLE)
        if not token:
            raise ValueError("No valid Gmail token found")
        
        return build(
            'gmail',
            'v1',
            credentials=Credentials(
                token=token.access_token,
                refresh_token=token.refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.GOOGLE_CLIENT_ID,
                client_secret=settings.GOOGLE_CLIENT_SECRET
            )
        )
        
    async def send_email(self, user_id: str, message: EmailMessage) -> Dict[str, Any]:
        """Send an email"""
        try:
            service = await self.get_client(user_id)
            
            msg = MIMEMultipart()
            msg['to'] = ', '.join(message.to)
            msg['subject'] = message.subject
            
            if message.cc:
                msg['cc'] = ', '.join(message.cc)
                
            if message.bcc:
                msg['bcc'] = ', '.join(message.bcc)
                
            if message.body_type == "html":
                msg.attach(MIMEText(message.body, 'html'))
            else:
                msg.attach(MIMEText(message.body, 'plain'))
                
            if message.attachments:
                for attachment in message.attachments:
                    part = MIMEBase(*attachment.content_type.split("/"))
                    part.set_payload(base64.b64decode(attachment.data))
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {attachment.filename}"
                    )
                    msg.attach(part)

            raw_message = base64.urlsafe_b64encode(
                msg.as_bytes()
            ).decode('utf-8')

            message = service.users().messages().send(
                userId="me",
                body={"raw": raw_message}
            ).execute()

            return {
                "message_id": message["id"],
                "thread_id": message["threadId"]
            }

        except HttpError as error:
            raise Exception(f"Failed to send email: {error}")
                
    async def read_emails(
        self,
        user_id: str,
        filter_params: GmailFilter,
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """Read emails based on filters"""
        try:
            service = await self.get_client(user_id)
            
            # Build query string
            query_parts = []
            if filter_params.from_:
                query_parts.append(f"from:{filter_params.from_}")
            if filter_params.to:
                query_parts.append(f"to:{filter_params.to}")
            if filter_params.subject:
                query_parts.append(f"subject:{filter_params.subject}")
            if filter_params.has_attachment:
                query_parts.append("has:attachment")
            if filter_params.label:
                query_parts.append(f"label:{filter_params.label}")
            if filter_params.after:
                query_parts.append(f"after:{filter_params.after}")
            if filter_params.before:
                query_parts.append(f"before:{filter_params.before}")

            query = " ".join(query_parts)

            messages = []
            request = service.users().messages().list(
                userId="me",
                q=query,
                maxResults=max_results
            )

            while request is not None:
                response = request.execute()
                message_list = response.get("messages", [])
                
                for msg in message_list:
                    message = service.users().messages().get(
                        userId="me",
                        id=msg["id"],
                        format="full"
                    ).execute()
                    
                    messages.append(self._parse_message(message))
                    
                request = service.users().messages().list_next(
                    request,
                    response
                )

            return messages

        except HttpError as error:
            raise Exception(f"Failed to read emails: {error}")
    
    def _parse_message(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Gmail message into structured format"""
        headers = message["payload"]["headers"]
        
        # Extract headers
        subject = next(
            (h["value"] for h in headers if h["name"].lower() == "subject"),
            ""
        )
        from_ = next(
            (h["value"] for h in headers if h["name"].lower() == "from"),
            ""
        )
        to = next(
            (h["value"] for h in headers if h["name"].lower() == "to"),
            ""
        )
        date = next(
            (h["value"] for h in headers if h["name"].lower() == "date"),
            ""
        )

        # Extract body
        body = self._get_message_body(message["payload"])

        return {
            "id": message["id"],
            "thread_id": message["threadId"],
            "subject": subject,
            "from": from_,
            "to": to,
            "date": date,
            "body": body,
            "labels": message["labelIds"]
        }
    
    def _get_message_body(self, payload: Dict[str, Any]) -> str:
        """Extract message body from payload"""
        if "body" in payload and payload["body"].get("data"):
            return base64.urlsafe_b64decode(
                payload["body"]["data"]
            ).decode('utf-8')
            
        if "parts" in payload:
            for part in payload["parts"]:
                if part["mimeType"] in ["text/plain", "text/html"]:
                    if "data" in part["body"]:
                        return base64.urlsafe_b64decode(
                            part["body"]["data"]
                        ).decode('utf-8')
                        
        return ""
