from framework.services.service_factory import BaseServiceFactory
# import app.resources.course_resource as course_resource
import app.resources.chat_resource as chat_resource
from framework.services.data_access.MySQLRDBDataService import MySQLRDBDataService
import dotenv, os

dotenv.load_dotenv()
user = os.getenv('DB_USER')
password = os.getenv('DB_PASS')
host = os.getenv('DB_HOST')
port = int(os.getenv('DB_PORT'))


class ServiceFactory(BaseServiceFactory):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_service(cls, service_name):

        if service_name == 'ChatResource':
            result = chat_resource.ChatResource(config=None)
        elif service_name == 'ChatResourceDataService':
            context = dict(user=user, password=password, host=host, port=port)
            data_service = MySQLRDBDataService(context=context)
            result = data_service
        else:
            result = None

        return result




