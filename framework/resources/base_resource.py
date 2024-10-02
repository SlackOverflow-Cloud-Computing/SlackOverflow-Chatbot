from abc import ABC, abstractmethod, abstractclassmethod
from typing import Any


class BaseResource(ABC):

    def __init__(self, config):
        self.config = config

    @abstractmethod
    def get_info_by_key(self, key: str) -> Any:
        raise NotImplementedError()

    @abstractmethod
    def get_details_by_key(self, key: str) -> Any:
        raise NotImplementedError()


