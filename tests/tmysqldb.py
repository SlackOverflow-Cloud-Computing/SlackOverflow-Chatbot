from app.resources.chat_resource import ChatResource
from app.services.service_factory import ServiceFactory
import json


def test_get_chats_by_chat_id():
    chat_id = "707dcd66-30e3-4fc7-a25d-d570d2ccfcda"
    res = ServiceFactory.get_service("ChatResource")
    result = res._get_chats_by_key(key_field="chat_id", key=chat_id)
    print(result)


def test_get_chats_by_role():
    role = "ai"
    res = ServiceFactory.get_service("ChatResource")
    result = res._get_chats_by_key(key_field="role", key=role)
    print(result)


def test_get_chat_ids():
    user_id = "8fa98871-2e6a-42e1-b602-00050e5a0ac4"
    res = ServiceFactory.get_service("ChatResource")
    result = res._get_chat_ids(key=user_id)
    print(result)

def test_get_chat_ids_agent():
    user_id = "8fa98871-2e6a-42e1-b602-00050e5a0ac4"
    res = ServiceFactory.get_service("ChatResource")
    result = res._get_chat_ids(key=user_id, agent_name="Recommendation")
    print(result)


def test_analyze_preference():
    user_id = "8fa98871-2e6a-42e1-b602-00050e5a0ac4"
    db_service = ServiceFactory.get_service("ChatResource")
    chat_history = db_service.get_chat_history(user_id=user_id, chat_id=None, role="human",
                                               agent_name="Recommendation")

    if chat_history:
        openai_service = ServiceFactory.get_service("OpenAI")
        result = openai_service.analyze_user_preference(chat_history)
        print(result)
