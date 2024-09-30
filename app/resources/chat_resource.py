from typing import Any

from framework.resources.base_resource import BaseResource

from app.models.chat_info import ChatInfo
from app.models.chat_details import ChatDetails
from app.services.service_factory import ServiceFactory


class ChatResource(BaseResource):

    def __init__(self, config):
        super().__init__(config)

        # TODO -- Replace with dependency injection.
        #
        self.data_service = ServiceFactory.get_service("ChatResourceDataService")
        self.database = "TODO"
        self.info_collection = "TODO"
        self.details_collection = "TODO"
        self.info_key_field = "chat_id"
        self.details_key_field = "line_id"

    def get_info_by_key(self, key: str) -> ChatInfo:

        d_service = self.data_service

        result = d_service.get_data_object(
            self.database, self.info_collection, key_field=self.info_key_field, key_value=key
        )

        result = ChatInfo(**result)
        return result

    def get_details_by_key(self, key: str) -> ChatDetails:

        d_service = self.data_service

        result = d_service.get_data_object(
            self.database, self.details_collection, key_field=self.details_key_field, key_value=key
        )

        result = ChatDetails(**result)
        return result

