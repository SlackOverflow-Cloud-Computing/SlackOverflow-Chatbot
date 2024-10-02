from framework.services.service_factory import BaseServiceFactory
# import app.resources.course_resource as course_resource
import app.resources.chat_resource as chat_resource
from framework.services.data_access.MySQLRDBDataService import MySQLRDBDataService


# TODO -- Implement this class
class ServiceFactory(BaseServiceFactory):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_service(cls, service_name):

        if service_name == 'ChatResource':
            result = chat_resource.ChatResource(config=None)
        elif service_name == 'ChatResourceDataService':
            context = dict(user="admin", password="slackOverflowDB",
                           host="database-1.ccjxezwbfect.us-east-1.rds.amazonaws.com", port=3306)
            data_service = MySQLRDBDataService(context=context)
            result = data_service
        else:
            result = None

        return result




