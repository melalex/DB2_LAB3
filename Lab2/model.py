import re
import mysql.connector

from DB1_LAB2.settings import lab2_config


def delete_suffix(path):
    if path.endswith("__lt") or \
            path.endswith("__le") or \
            path.endswith("__gt") or \
            path.endswith("__ge") or \
            path.endswith("__ne"):
        result = path[:-4]
    else:
        result = path
    return result


def delete_suffix_decorator(class_method):
    def wrapper(cls, path, max_level):
        attribute = delete_suffix(path)
        return class_method(cls, attribute, max_level)
    return wrapper


class Model(object):
    __connection = mysql.connector.connect(**lab2_config)
    __cursor = __connection.cursor()

    entity_id = int

    @classmethod
    @delete_suffix_decorator
    def __get_attribute(cls, path, max_level):
        path_list = path.split('__')
        if len(path_list) > max_level:
            return None
        return reduce(lambda obj, attr: getattr(obj, attr, None), path_list, cls)

    @classmethod
    def __get_class_vars(cls):
        return {key: value for key, value in cls.__dict__.items() if not key.startswith('__') and not callable(key)}

    @classmethod
    def __type_validation(cls, max_level, **kwargs):
        for key, value in kwargs:
            value_type = cls.__get_attribute(key, max_level)
            if not (value_type and ((type(value) is value_type) or (issubclass(value, Model) and type(value) is int))):
                return False
        return True

    @classmethod
    def __column_validation(cls, max_level, *args):
        for column in args:
            if not cls.__get_attribute(column, max_level):
                return False
        return True

    @classmethod
    def __translate_into_sql(cls, attribute):
        sql_attribute = delete_suffix(attribute).replace("__", ".")
        prefix = (cls.__name__ + '.') if '.' in attribute else ''
        return "%s%s" % (prefix, sql_attribute)

    @classmethod
    def __where(cls, **kwargs):
        where_part = " WHERE"
        for key, value in kwargs:
            if key.endswith("__lt"):
                operator = '<'
            elif key.endswith("__le"):
                operator = '<='
            elif key.endswith("__gt"):
                operator = '>'
            elif key.endswith("__ge"):
                operator = '>='
            elif key.endswith("__ne"):
                operator = '!='
            else:
                operator = '='
            attribute = cls.__translate_into_sql(key)
            where_part += " %s %s %s AND" % (attribute, operator, value)
        return where_part[:-4] if len(where_part) > 6 else ""

    @classmethod
    def insert(cls, **kwargs):
        if not cls.__type_validation(1, **kwargs):
            raise ValueError

        columns = str(kwargs.keys())[1:-1]
        insert_values = re.sub(
            r"(^[\w]+,)|( [\w]+,)|( [\w]$)",
            lambda match_obj: "%(%s)s," % match_obj.group(0),
            columns
        )

        insert_values = insert_values[:-1]
        query = "INSERT INTO %s(%s) VALUES(%s)" % (cls.__name__, columns, insert_values)
        cls.__cursor.execute(query, kwargs)

        return cls.__cursor.lastrowid

    @classmethod
    def select(cls, *args, **kwargs):
        if not (cls.__type_validation(2, **kwargs) and cls.__column_validation(2, args)):
            raise ValueError

    @classmethod
    def update(cls):
        pass

    @classmethod
    def delete(cls):
        pass
