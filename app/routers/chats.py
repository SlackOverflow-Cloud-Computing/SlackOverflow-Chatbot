from fastapi import APIRouter, status, HTTPException, Query, Request
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import logging

from app.models.chat_details import ChatDetails
from app.models.chat_info import ChatInfo
from app.models.traits import Message, Traits
from app.resources.chat_resource import ChatResource
from app.services.service_factory import ServiceFactory

router = APIRouter()
logger = logging.getLogger("uvicorn")

class ChatData(BaseModel):
    chat_id: Optional[str] = None
    role: Optional[str] = None
    content: Optional[str] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None
    agent_id: Optional[str] = None
    agent_name: Optional[str] = None

class ChatResponse(BaseModel):
    content: str
    traits: Optional[Traits]


@router.get("/chat_info/{chat_id}", tags=["chat"], status_code=status.HTTP_200_OK)
async def get_chat_info(chat_id: str, request: Request) -> ChatInfo:
    """Get chat details by chat id"""
    cid = request.headers.get("X-Correlation-ID")
    logger.info(f"Incoming Request - Method: GET, Path: /chat_info/{chat_id} - [{cid}]")
    res = ServiceFactory.get_service("ChatResource")
    result = res.get_info_by_key(chat_id)
    if result is None:
        logger.error(f"Couldn't find chat with id {chat_id} - [{cid}]")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return result


@router.get("/chat_details/{message_id}", tags=["chat"], status_code=status.HTTP_200_OK)
async def get_chat_details(message_id: str, request: Request) -> ChatDetails:
    """Gets chat details by message id"""
    cid = request.headers.get("X-Correlation-ID")
    logger.info(f"Incoming Request - Method: GET, Path: /chat_details/{message_id} - [{cid}]")
    res = ServiceFactory.get_service("ChatResource")
    result = res.get_details_by_key(message_id)
    if result is None:
        logger.error(f"Couldn't find message details with id {message_id} - [{cid}]")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat details not found")
    return result


@router.get("/chat_history", tags=["chat"], response_model=List[ChatDetails], status_code=status.HTTP_200_OK)
async def get_chat_history(
    request: Request,
    user_id: str = Query(..., description="User ID (required)"),
    chat_id: Optional[str] = Query(None, description="Chat ID to optionally filter by"),
    role: Optional[str] = Query(None, description="Role to optionally filter by"),
    agent_name: Optional[str] = Query(None, description="Agent Name to optionally filter by")
) -> List[ChatDetails]:
    """Get chat history by user_id (optional: chat_id, agent_type and role), return messages list."""
    cid = request.headers.get("X-Correlation-ID")
    logger.info(f"Incoming Request - Method: GET, Path: /chat_history - [{cid}]")
    res = ServiceFactory.get_service("ChatResource")
    result = res.get_chat_history(user_id=user_id, chat_id=chat_id, role=role, agent_name=agent_name)

    if not result:
        logger.error(f"No chat details found for user_id/chat_id: {user_id}/{chat_id} - [{cid}]")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No chat details found for user_id: {user_id}"
        )
    return result


@router.post("/update_chat", tags=["chat"], status_code=status.HTTP_200_OK)
async def update_chat(chat_data: ChatData, request: Request) -> str:
    """Store message to database, return a chat_id"""
    cid = request.headers.get("X-Correlation-ID")
    logger.info(f"Incoming Request - Method: POST, Path: /update_chat - [{cid}]")
    res = ServiceFactory.get_service("ChatResource")
    result = res.update_chat(chat_data)
    if result is None:
        logger.error(f"Failed to add new chat message to database: {chat_data} - [{cid}]")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Failed to add message to database")
    return result


@router.post("/general_chat", tags=["chat"], response_model=ChatResponse, status_code=status.HTTP_200_OK)
async def general_chat(
    request: Request,
    user_id: str = Query(..., description="User ID (required)"),
    chat_id: str = Query(None, description="Chat ID (optional)"),
    query: str = Query(..., description="Chat Input (required)"),
) -> ChatResponse:
    """Generate the multiple rounds chat with user and determine when to give the recommendation"""
    cid = request.headers.get("X-Correlation-ID")
    logger.info(f"Incoming Request - Method: POST, Path: /general_chat - [{cid}]")
    
    # Get chat history by specific chat id
    db_service = ServiceFactory.get_service("ChatResource")
    chat_history = db_service.get_chat_history(user_id=user_id, chat_id=chat_id, agent_name="Chat")

    # Generate agent's answer
    openai_service = ServiceFactory.get_service("OpenAI")
    answer = openai_service.general_chat(query=query, chat_history=chat_history, cid=cid)
    if answer is None:
        logger.error(f"Couldn't get Open AI response - [{cid}]")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Couldn't get Open AI response")

    if answer["need_recommendation"]: # able to generate recommendation:
        traits = openai_service.extract_song_traits(query, cid)
        if traits is None:
            logger.error(f"Couldn't get song traits - [{cid}]")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Couldn't extract song traits")
        response_data = ChatResponse(
            content=answer["content"],
            traits=traits
        )
        return response_data
    else: # continue general chat
        if answer["content"] is None:
            logger.error(f"Failed generating chat content - [{cid}]")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed in generating chat content")
        response_data = ChatResponse(
            content=answer["content"],
            traits=None
        )
        return response_data



@router.post("/analyze_preference", tags=["analyze preference"], status_code=status.HTTP_200_OK)
async def analyze_preference(
    request: Request,
    user_id: str = Query(..., description="User ID (required)"),
    chat_id: Optional[str] = Query(None, description="Chat ID (optional)"),
) -> str:
    """Analyze the user preference with given chat history, return agent message"""
    cid = request.headers.get("X-Correlation-ID")
    logger.info(f"Incoming Request - Method: POST, Path: /analyze_preference - [{cid}]")
    
    # Get chat history with human input and recommendation only
    db_service = ServiceFactory.get_service("ChatResource")
    chat_history = db_service.get_chat_history(user_id=user_id, chat_id=chat_id, role="human", agent_name="Chat")

    if chat_history:
        # Get preference analysis
        openai_service = ServiceFactory.get_service("OpenAI")
        result = openai_service.analyze_user_preference(chat_history, cid)
        if result is None:
            logger.error(f"Unable to analyze the user's preference - [{cid}]")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unable to analyze the user's preference")
    else:
        logger.error(f"No user records available for analysis - [{cid}]")
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No user records available for analysis")

    # print(f"chatbot service - result: {result}")
    return result


@router.post("/extract_traits", tags=["extract traits"], response_model=Traits, status_code=status.HTTP_200_OK)
async def extract_traits(query: Message, request: Request) -> Traits:
    """Given a user query, return a formatted spotify recommendations JSON"""
    cid = request.headers.get("X-Correlation-ID")
    logger.info(f"Incoming Request - Method: POST, Path: /extract_traits - [{cid}]")
    result = ServiceFactory.get_service("OpenAI")
    result = result.extract_song_traits(query.query, cid)
    if result is None:
        logger.error(f"Couldn't extract song traits - [{cid}]")
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Couldn't extract song traits")
    return result

