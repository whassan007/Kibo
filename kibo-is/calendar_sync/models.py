from pydantic import BaseModel
from typing import Optional, Literal
import datetime

class CalendarEvent(BaseModel):
    user_id: str
    task_id: str
    title: str
    start: datetime.datetime
    end: datetime.datetime
    description: Optional[str] = None
    provider: Literal["microsoft", "google"]
    visibility: Literal["private", "public"] = "private"
