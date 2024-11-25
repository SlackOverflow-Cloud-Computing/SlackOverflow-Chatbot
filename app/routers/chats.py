from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.models.chat_details import ChatDetails
from app.models.chat_info import ChatInfo
from app.models.traits import Message, Traits
from app.resources.chat_resource import ChatResource
from app.services.service_factory import ServiceFactory

router = APIRouter()

class ChatData(BaseModel):
    chat_id: Optional[str] = None
    role: Optional[str] = None
    content: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None

@router.get("/chat_info/{chat_id}", tags=["chat"], status_code=status.HTTP_200_OK)
async def get_chat_info(chat_id: str) -> ChatInfo:
    res = ServiceFactory.get_service("ChatResource")
    result = res.get_info_by_key(chat_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return result


@router.get("/chat_details/{message_id}", tags=["chat"], status_code=status.HTTP_200_OK)
async def get_chat_details(message_id: str) -> ChatDetails:
    res = ServiceFactory.get_service("ChatResource")
    result = res.get_details_by_key(message_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat details not found")
    return result

@router.post("/update_chat", tags=["chat"], status_code=status.HTTP_200_OK)
async def update_chat(chat_data: ChatData) -> str:
    """Store message to database, return a chat_id"""
    res = ServiceFactory.get_service("ChatResource")
    result = res.update_chat(chat_data)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Failed to add message to database")
    return result

@router.post("/extract_traits", tags=["extract traits"], response_model=Traits, status_code=status.HTTP_200_OK)
async def extract_traits(query: Message) -> Traits:
    """Given a user query, return a formatted spotify recommendations JSON"""
    result = ServiceFactory.get_service("OpenAI")
    result = result.extract_song_traits(query.query)
    if result is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Couldn't extract song traits")
    return result

