import pymysql
from .BaseDataService import DataDataService


class MySQLRDBDataService(DataDataService):
    """
    A generic data service for MySQL databases. The class implement common
    methods from BaseDataService and other methods for MySQL. More complex use cases
    can subclass, reuse methods and extend.
    """

    def __init__(self, context):
        super().__init__(context)

    def _get_connection(self):
        connection = pymysql.connect(
            host=self.context["host"],
            port=self.context["port"],
            user=self.context["user"],
            passwd=self.context["password"],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        return connection

    def get_data_object(self,
                        database_name: str,
                        collection_name: str,
                        key_field: str,
                        key_value: str):
        """
        See base class for comments.
        """

        connection = None
        result = None

        try:
            sql_statement = f"SELECT * FROM {database_name}.{collection_name} " + \
                            f"where {key_field}=%s"
            connection = self._get_connection()
            cursor = connection.cursor()
            cursor.execute(sql_statement, [key_value])
            result = cursor.fetchone()
        except Exception as e:
            print(f"Error getting data into {database_name}.{collection_name}: {e}")
            if connection:
                connection.close()

        return result

    def add_data_object(self,
                        database_name: str,
                        collection_name: str,
                        data: dict):

        connection = None
        result = None

        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join(['%s'] * len(data))
            sql_statement = f"INSERT INTO {database_name}.{collection_name} ({columns}) VALUES ({placeholders})"
            values = list(data.values())

            connection = self._get_connection()
            cursor = connection.cursor()
            cursor.execute(sql_statement, values)

            if 'chat_id' in data:
                result = data['chat_id']
            elif 'message_id' in data:
                result = data['message_id']
            else:
                result = cursor.lastrowid

        except Exception as e:
            print(f"Error inserting data into {database_name}.{collection_name}: {e}")
            if connection:
                connection.rollback()
        finally:
            if connection:
                connection.close()

        return result

    def update_data_object(self,
                           database_name: str,
                           collection_name: str,
                           key_field: str,
                           key_value: str,
                           update_data: dict):

        connection = None
        result = None

        try:
            set_clause = ', '.join([f"{field}=%s" for field in update_data.keys()])
            sql_statement = f"UPDATE {database_name}.{collection_name} SET {set_clause} WHERE {key_field}=%s"
            values = list(update_data.values()) + [key_value]

            connection = self._get_connection()
            cursor = connection.cursor()
            cursor.execute(sql_statement, values)

            result = cursor.fetchone()
            # connection.commit()
            # result = cursor.rowcount

        except Exception as e:
            print(f"Error updating data in {database_name}.{collection_name}: {e}")
            if connection:
                connection.rollback()
        finally:
            if connection:
                connection.close()

        return result
