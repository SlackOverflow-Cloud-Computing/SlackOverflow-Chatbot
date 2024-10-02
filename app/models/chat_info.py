from __future__ import annotations

from typing import Optional

from pydantic import BaseModel
from datetime import datetime


class ChatInfo(BaseModel):
    chat_id: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None
    created_at: Optional[datetime] = None


    class Config:
        json_schema_extra = {
            "example": {
                "chat_id": "e19aca8d-885f-4beb-83d4-1ff89b392aea",
                "user_id": "8a0b8704-e599-4ea9-be7e-4453e5b69b31",
                "user_name": "xxx",
                "agent_id": "c4eae483-2001-487e-89e4-6d91a71c8478",
                "agent_name": "Agent_A",
                "created_at": "2024-04-05T00:58:50Z",
            }
        }
