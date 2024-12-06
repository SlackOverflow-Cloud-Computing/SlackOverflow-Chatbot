from typing import Any, Optional

from framework.resources.base_resource import BaseResource

from app.models.chat_info import ChatInfo
from app.models.chat_details import ChatDetails
from app.services.service_factory import ServiceFactory
import dotenv, os
import uuid
from datetime import datetime

dotenv.load_dotenv()
db = os.getenv('DB_NAME')
info_collection = os.getenv('DB_INFO_COLLECTION')
details_collection = os.getenv('DB_DETAILS_COLLECTION')


class ChatResource(BaseResource):

    def __init__(self, config):
        super().__init__(config)

        self.data_service = ServiceFactory.get_service("ChatResourceDataService")
        self.database = db
        self.info_collection = info_collection
        self.details_collection = details_collection
        self.info_key_field = "chat_id"
        self.details_key_field = "message_id"
        self.user_key_filed = "user_id"

    def get_info_by_key(self, key: str) -> ChatInfo:
        d_service = self.data_service

        result = d_service.get_data_object(
            self.database, self.info_collection, key_field=self.info_key_field, key_value=key
        )
        print(result)
        if result:
            result = ChatInfo(**result)
        return result

    def get_details_by_key(self, key: str) -> ChatDetails:
        d_service = self.data_service

        result = d_service.get_data_object(
            self.database, self.details_collection, key_field=self.details_key_field, key_value=key
        )

        if result:
            result = ChatDetails(**result)
        return result

    def _get_chat_ids(self, key: str, agent_name: Optional[str] = None) -> list[str]:
        d_service = self.data_service

        chat_info_list = d_service.get_all_data_object(
            self.database, self.info_collection, key_field=self.user_key_filed, key_value=key
        )

        if agent_name:
            chat_info_list = [info for info in chat_info_list if info["agent_name"] == agent_name]

        results = [info["chat_id"] for info in chat_info_list if "chat_id" in info]

        return results

    def _get_chats_by_key(self, key_field: str, key: str) -> list[ChatDetails]:
        d_service = self.data_service

        results = d_service.get_all_data_object(
            self.database, self.details_collection, key_field=key_field, key_value=key
        )
        if results:
            for i in range(len(results)):
                result = results.pop(0)
                if result:
                    result = ChatDetails(**result)
                results.append(result)
        return results

    def get_chat_history(self,
                         user_id: str,
                         chat_id: Optional[str],
                         role: Optional[str],
                         agent_name: Optional[str]) -> list[ChatDetails]:
        result = []
        chat_ids = self._get_chat_ids(key=user_id, agent_name=agent_name)

        if not chat_ids:
            return result

        if chat_id:
            chat_details = self._get_chats_by_key(key_field="chat_id", key=chat_id)
            result += chat_details
        else:
            for chat_id in chat_ids:
                chat_details = self._get_chats_by_key(key_field="chat_id", key=chat_id)
                result += chat_details

        if role:
            result = [item for item in result if item.role == role]

        return result

    def update_chat(self, chat_data) -> str:
        message_id = str(uuid.uuid4())
        created_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        # Check whether a new chat_id
        info_result = self.get_info_by_key(chat_data.chat_id)

        if info_result is None:
            chat_info_data = {
                "chat_id": chat_data.chat_id,
                "user_id": chat_data.user_id,
                "user_name": chat_data.user_name,
                "agent_id": chat_data.agent_id,
                "agent_name": chat_data.agent_name,
                "created_at": created_at
            }
            info_id = self.data_service.add_data_object(
                database_name=self.database,
                collection_name=self.info_collection,
                data=chat_info_data
            )
            info_result = self.get_info_by_key(info_id)
            # print(f"info_result: {info_result}")

        # Add to chat_details
        chat_details_data = {
            "message_id": message_id,
            "chat_id": chat_data.chat_id,
            "role": chat_data.role,
            "content": chat_data.content,
            "created_at": created_at
        }

        details_result = self.data_service.add_data_object(
            database_name=self.database,
            collection_name=self.details_collection,
            data=chat_details_data
        )

        return info_result.chat_id
