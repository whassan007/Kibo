import httpx
import json
from typing import Any, Dict
from pathlib import Path
from ..db import get_connection
from ..models import CalendarEvent

# Placeholder encryption/decryption (no-op for demo)
def _decrypt_token(encrypted: bytes) -> str:
    return encrypted.decode('utf-8')

def _get_user_token(user_id: str, provider: str) -> str:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT encrypted_token FROM user_tokens WHERE user_id=? AND provider=?",
        (user_id, provider),
    )
    row = cur.fetchone()
    conn.close()
    if not row:
        raise Exception(f"No token found for user {user_id} provider {provider}")
    return _decrypt_token(row["encrypted_token"])

class MicrosoftGraphProvider:
    base_url = "https://graph.microsoft.com/v1.0"

    async def create_event(self, event: CalendarEvent) -> str:
        token = _get_user_token(event.user_id, "microsoft")
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {
            "subject": event.title,
            "body": {"contentType": "HTML", "content": event.description or ""},
            "start": {"dateTime": event.start.isoformat(), "timeZone": "UTC"},
            "end": {"dateTime": event.end.isoformat(), "timeZone": "UTC"},
            "sensitivity": "private" if event.visibility == "private" else "normal",
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{self.base_url}/me/events", headers=headers, json=payload)
            resp.raise_for_status()
            data = resp.json()
            return data.get("id")

    async def update_event(self, event_id: str, updates: Dict[str, Any]):
        # For simplicity, we re-use the same payload structure as create_event
        token = _get_user_token(updates.get("user_id", ""), "microsoft")
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        payload = {}
        if "title" in updates:
            payload["subject"] = updates["title"]
        if "description" in updates:
            payload["body"] = {"contentType": "HTML", "content": updates["description"]}
        if "start" in updates:
            payload["start"] = {"dateTime": updates["start"].isoformat(), "timeZone": "UTC"}
        if "end" in updates:
            payload["end"] = {"dateTime": updates["end"].isoformat(), "timeZone": "UTC"}
        if "visibility" in updates:
            payload["sensitivity"] = "private" if updates["visibility"] == "private" else "normal"
        async with httpx.AsyncClient() as client:
            resp = await client.patch(f"{self.base_url}/me/events/{event_id}", headers=headers, json=payload)
            resp.raise_for_status()

    async def delete_event(self, event_id: str):
        token = _get_user_token("", "microsoft")  # token retrieval expects user_id; in real code store user per event
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient() as client:
            resp = await client.delete(f"{self.base_url}/me/events/{event_id}", headers=headers)
            resp.raise_for_status()
