"""Meta Cloud API WhatsApp client."""

import logging
from typing import Optional
import httpx
from app.config import settings

logger = logging.getLogger(__name__)

BASE_URL = f"https://graph.facebook.com/{settings.META_API_VERSION}"


class WhatsAppClient:
    """Client for Meta WhatsApp Cloud API."""

    def __init__(self, access_token: str = "", phone_number_id: str = ""):
        self.access_token = access_token or settings.META_WHATSAPP_TOKEN
        self.phone_number_id = phone_number_id or settings.META_PHONE_NUMBER_ID
        self.test_mode = not self.access_token

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

    async def send_text_message(self, to: str, text: str) -> dict:
        """Send a text message to a WhatsApp number."""
        if self.test_mode:
            logger.info(f"[TEST MODE] Send to {to}: {text}")
            return {"messaging_product": "whatsapp", "test_mode": True, "to": to, "text": text}

        url = f"{BASE_URL}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"preview_url": False, "body": text},
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self._headers())
            response.raise_for_status()
            return response.json()

    async def send_template_message(
        self, to: str, template_name: str, language: str = "en",
        components: Optional[list] = None
    ) -> dict:
        """Send a template message."""
        if self.test_mode:
            logger.info(f"[TEST MODE] Template '{template_name}' to {to}")
            return {"test_mode": True, "template": template_name, "to": to}

        url = f"{BASE_URL}/{self.phone_number_id}/messages"
        template = {"name": template_name, "language": {"code": language}}
        if components:
            template["components"] = components
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": template,
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self._headers())
            response.raise_for_status()
            return response.json()

    async def send_interactive_message(self, to: str, body: str, buttons: list) -> dict:
        """Send an interactive button message."""
        if self.test_mode:
            logger.info(f"[TEST MODE] Interactive to {to}: {body}")
            return {"test_mode": True, "to": to, "body": body, "buttons": buttons}

        url = f"{BASE_URL}/{self.phone_number_id}/messages"
        payload = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": body},
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": b["id"], "title": b["title"]}}
                        for b in buttons[:3]  # WhatsApp max 3 buttons
                    ]
                },
            },
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=self._headers())
            response.raise_for_status()
            return response.json()

    async def send_payment_link(self, to: str, product_name: str, amount: float,
                                 currency: str, payment_url: str) -> dict:
        """Send a payment link message."""
        text = (
            f"💳 Payment for *{product_name}*\n"
            f"Amount: {currency} {amount:.2f}\n\n"
            f"Pay here: {payment_url}\n\n"
            f"Link expires in 24 hours."
        )
        return await self.send_text_message(to, text)

    @staticmethod
    def verify_webhook(mode: str, token: str, challenge: str) -> Optional[str]:
        """Verify Meta webhook subscription."""
        if mode == "subscribe" and token == settings.META_VERIFY_TOKEN:
            return challenge
        return None

    @staticmethod
    def parse_webhook_payload(payload: dict) -> list:
        """Parse incoming webhook payload into message events."""
        messages = []
        for entry in payload.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                if "messages" not in value:
                    continue
                metadata = value.get("metadata", {})
                phone_number_id = metadata.get("phone_number_id")
                for msg in value.get("messages", []):
                    contact = value.get("contacts", [{}])[0]
                    messages.append({
                        "phone_number_id": phone_number_id,
                        "from": msg.get("from"),
                        "message_id": msg.get("id"),
                        "timestamp": msg.get("timestamp"),
                        "type": msg.get("type", "text"),
                        "text": msg.get("text", {}).get("body", ""),
                        "contact_name": contact.get("profile", {}).get("name", ""),
                    })
        return messages


# Singleton
whatsapp_client = WhatsAppClient()
