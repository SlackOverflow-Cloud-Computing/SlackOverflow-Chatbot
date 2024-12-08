#
# Placeholder for implementing the service factory and service locator patterns.
#
# https://medium.com/javarevisited/service-locator-factory-pattern-7bb9e835b709
#
from abc import ABC, abstractmethod



class BaseServiceFactory(ABC):

    def __init__(self):
        pass

    @classmethod
    @abstractmethod
    def get_service(cls, service_name):
        raise NotImplementedError()


