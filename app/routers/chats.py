from fastapi import APIRouter

from app.models.chat_details import ChatDetails
from app.models.chat_info import ChatInfo
# from app.resources.course_resource import CourseResource
from app.resources.chat_resource import ChatResource
from app.services.service_factory import ServiceFactory

router = APIRouter()


@router.get("/chat_info/{chat_id}", tags=["info"])
async def get_chat_info(chat_id: int) -> ChatInfo:
    res = ServiceFactory.get_service("ChatResource")
    result = res.get_info_by_key(chat_id)
    return result


@router.get("/chat_details/{line_id}", tags=["detail"])
async def get_chat_details(line_id: int) -> ChatDetails:
    res = ServiceFactory.get_service("ChatResource")
    result = res.get_details_by_key(line_id)
    return result

