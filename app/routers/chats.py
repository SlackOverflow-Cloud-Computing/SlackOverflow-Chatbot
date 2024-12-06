from fastapi import APIRouter, status, HTTPException, Query
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


@router.get("/chat_history", tags=["chat"], response_model=list[ChatDetails], status_code=status.HTTP_200_OK)
async def get_chat_history(
    user_id: str = Query(..., description="User ID (required)"),
    chat_id: Optional[str] = Query(None, description="Chat ID to optionally filter by"),
    role: Optional[str] = Query(None, description="Role to optionally filter by"),
    agent_name: Optional[str] = Query(None, description="Agent Name to optionally filter by")
) -> list[ChatDetails]:
    """Get chat history by user_id (optional: chat_id, agent_type and role), return messages list."""

    res = ServiceFactory.get_service("ChatResource")
    result = res.get_chat_history(user_id=user_id, chat_id=chat_id, role=role, agent_name=agent_name)

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No chat details found for user_id: {user_id}"
        )
    return result


@router.post("/update_chat", tags=["chat"], status_code=status.HTTP_200_OK)
async def update_chat(chat_data: ChatData) -> list[ChatDetails]:
    """Store message to database, return a chat_id"""
    res = ServiceFactory.get_service("ChatResource")
    result = res.update_chat(chat_data)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Failed to add message to database")
    return result

@router.post("/analyze_preference", tags=["analyze preference"], status_code=status.HTTP_200_OK)
async def analyze_preference(
    user_id: str = Query(..., description="User ID (required)"),
    chat_id: Optional[str] = Query(None, description="Chat ID (optional)"),
) -> str:
    """Analyze the user preference with given chat history, return agent message"""

    # Get chat history with human input and recommendation only
    db_service = ServiceFactory.get_service("ChatResource")
    chat_history = db_service.get_chat_history(user_id=user_id, chat_id=chat_id, role="human", agent_name="Recommendation")

    if chat_history:
        # Get preference analysis
        openai_service = ServiceFactory.get_service("OpenAI")
        result = openai_service.analyze_user_preference(chat_history)
        if result is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to analyze the user's preference")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user records available for analysis")

    return result


@router.post("/extract_traits", tags=["extract traits"], response_model=Traits, status_code=status.HTTP_200_OK)
async def extract_traits(query: Message) -> Traits:
    """Given a user query, return a formatted spotify recommendations JSON"""
    result = ServiceFactory.get_service("OpenAI")
    result = result.extract_song_traits(query.query)
    if result is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Couldn't extract song traits")
    return result

