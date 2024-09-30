from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


class ChatInfo(BaseModel):
    chat_id: Optional[int] = None
    user_id: Optional[int] = None
    user_name: Optional[str] = None
    agent_id: Optional[int] = None
    agent_name: Optional[str] = None
    created_at: Optional[str] = None


    class Config:
        json_schema_extra = {
            "example": {
                "chat_id": 1,
                "user_id": 1,
                "user_name": "xxx",
                "agent_id": 1,
                "agent_name": "Agent_A",
                "created_at": "2024-04-05T00:58:50Z",
            }
        }
