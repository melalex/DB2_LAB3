import re
import mysql.connector

from DB1_LAB2.settings import lab2_config


class Model(object):
    __connection = mysql.connector.connect(**lab2_config)
    __cursor = __connection.cursor()

    entity_id = int

    @classmethod
    def __get_attribute(cls, path):
        return reduce(lambda obj, attr: getattr(obj, attr, None), path.split('.'), cls)

    @classmethod
    def __get_class_vars(cls):
        return {key: value for key, value in cls.__dict__.items() if not key.startswith('__') and not callable(key)}

    @classmethod
    def __validation(cls, **kwargs):
        for key, value in kwargs:
            value_type = cls.__get_attribute(key)
            if not (value_type and ((type(value) is value_type) or (issubclass(value, Model) and type(value) is int))):
                return False
        return True

    @classmethod
    def insert(cls, **kwargs):
        if not cls.__validation(**kwargs):
            raise ValueError

        columns = str(kwargs.keys())[1:-1]
        insert_values = re.sub(
            r"(^[\w]+,)|( [\w]+,)|( [\w]$)",
            lambda match_obj: "%(%s)s," % match_obj.group(0),
            columns
        )

        insert_values = insert_values[:-1]
        query = "INSERT INTO %s(%s) VALUES(%s)" % cls.__name__, columns, insert_values
        cls.__cursor.execute(query, kwargs)

        return cls.__cursor.lastrowid

    @classmethod
    def select(cls):
        pass

    @classmethod
    def update(cls):
        pass

    @classmethod
    def delete(cls):
        pass
