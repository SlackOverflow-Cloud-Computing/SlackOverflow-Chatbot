from fastapi import APIRouter, status, HTTPException

from app.models.chat_details import ChatDetails
from app.models.chat_info import ChatInfo
# from app.resources.course_resource import CourseResource
from app.resources.chat_resource import ChatResource
from app.services.service_factory import ServiceFactory

router = APIRouter()


@router.get("/chat_info/{chat_id}", tags=["info"], status_code=status.HTTP_200_OK)
async def get_chat_info(chat_id: str) -> ChatInfo:
    res = ServiceFactory.get_service("ChatResource")
    result = res.get_info_by_key(chat_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return result


@router.get("/chat_details/{message_id}", tags=["detail"], status_code=status.HTTP_200_OK)
async def get_chat_details(message_id: str) -> ChatDetails:
    res = ServiceFactory.get_service("ChatResource")
    result = res.get_details_by_key(message_id)
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat details not found")
    return result

