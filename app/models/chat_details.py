from __future__ import annotations

from typing import Optional

from pydantic import BaseModel
from datetime import datetime


class ChatDetails(BaseModel):
    message_id: Optional[str] = None
    chat_id: Optional[str] = None
    role: Optional[str] = None
    content: Optional[str] = None
    created_at: Optional[datetime] = None


    class Config:
        json_schema_extra = {
            "example": {
                "message_id": "d0e11118-00a5-42ce-bf71-ec9187b61528",
                "chat_id": "e19aca8d-885f-4beb-83d4-1ff89b392aea",
                "role": "human",
                "content": "hi",
                "created_at": "2024-04-05T00:58:50Z",
            }
        }
