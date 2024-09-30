from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ChatDetails(BaseModel):
    message_id: Optional[int] = None
    chat_id: Optional[int] = None
    role: Optional[str] = None
    content: Optional[str] = None
    created_at: Optional[str] = None


    class Config:
        json_schema_extra = {
            "example": {
                "message_id": 1,
                "chat_id": 1,
                "role": "user",
                "content": "Hello world!",
                "created_at": "2024-04-05T00:58:50Z",
            }
        }
