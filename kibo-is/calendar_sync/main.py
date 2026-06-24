from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Literal, Optional
import datetime

from .db import get_connection, init_db
from .providers import get_provider

app = FastAPI(title="Calendar Sync Service", version="0.1.0")

# Ensure DB is ready on startup
@app.on_event("startup")
async def startup_event():
    init_db()

class CalendarPushRequest(BaseModel):
    user_id: str = Field(..., description="Internal user identifier")
    task_id: str = Field(..., description="Task/Ticket UUID that the event represents")
    title: str = Field(..., description="Event title")
    start: datetime.datetime = Field(..., description="ISO‑8601 start time (UTC)")
    end: datetime.datetime = Field(..., description="ISO‑8601 end time (UTC)")
    description: Optional[str] = Field(None, description="Event description")
    provider: Literal["microsoft", "google"] = Field(..., description="Calendar provider")
    visibility: Optional[Literal["private", "public"]] = Field("private")

@app.post("/push")
async def push_event(req: CalendarPushRequest):
    # Insert a pending record
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO calendar_pushes (user_id, task_id, provider, title, start, end, description, visibility)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            req.user_id,
            req.task_id,
            req.provider,
            req.title,
            req.start.isoformat(),
            req.end.isoformat(),
            req.description,
            req.visibility,
        ),
    )
    push_id = cur.lastrowid
    conn.commit()
    conn.close()

    # Immediate attempt to create the event via provider adapter
    provider = get_provider(req.provider)
    try:
        event_id = await provider.create_event(req)
        # Update record with external event id and success status
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE calendar_pushes SET event_id=?, status='sent', updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (event_id, push_id),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        # Mark as failed but keep payload for retry
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "UPDATE calendar_pushes SET status='failed', updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (push_id,),
        )
        conn.commit()
        conn.close()
        raise HTTPException(status_code=502, detail=f"Calendar provider error: {str(e)}")

    return {"push_id": push_id, "event_id": event_id}

class CalendarUpdateRequest(BaseModel):
    push_id: int = Field(..., description="Internal push record identifier")
    title: Optional[str]
    start: Optional[datetime.datetime]
    end: Optional[datetime.datetime]
    description: Optional[str]
    visibility: Optional[Literal["private", "public"]]

@app.put("/update")
async def update_event(req: CalendarUpdateRequest):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT provider, event_id FROM calendar_pushes WHERE id=?", (req.push_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Push record not found")
    provider_name, event_id = row["provider"], row["event_id"]
    if not event_id:
        raise HTTPException(status_code=400, detail="Event not yet created on provider")
    provider = get_provider(provider_name)
    # Build a partial payload for the provider
    update_payload = {k: v for k, v in req.dict().items() if k not in {"push_id"} and v is not None}
    try:
        await provider.update_event(event_id, update_payload)
        cur.execute(
            "UPDATE calendar_pushes SET updated_at=CURRENT_TIMESTAMP WHERE id=?",
            (req.push_id,),
        )
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Provider update failed: {str(e)}")
    finally:
        conn.close()
    return {"status": "updated"}

@app.delete("/delete/{push_id}")
async def delete_event(push_id: int):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT provider, event_id FROM calendar_pushes WHERE id=?", (push_id,))
    row = cur.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Push record not found")
    provider_name, event_id = row["provider"], row["event_id"]
    if not event_id:
        # Nothing to delete on provider, just remove record
        cur.execute("DELETE FROM calendar_pushes WHERE id=?", (push_id,))
        conn.commit()
        conn.close()
        return {"status": "removed"}
    provider = get_provider(provider_name)
    try:
        await provider.delete_event(event_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Provider delete failed: {str(e)}")
    # Delete local record
    cur.execute("DELETE FROM calendar_pushes WHERE id=?", (push_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}
