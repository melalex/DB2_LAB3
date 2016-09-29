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
    def wrapper(cls, path, separator):
        attribute = delete_suffix(path)
        return class_method(cls, attribute, separator)
    return wrapper


class Model(object):
    __connection = mysql.connector.connect(**lab2_config)
    __cursor = __connection.cursor()

    entity_id = int

    @classmethod
    @delete_suffix_decorator
    def __get_attribute(cls, path, separator):
        return reduce(lambda obj, attr: getattr(obj, attr, None), path.split(separator), cls)

    @classmethod
    def __get_class_vars(cls):
        return {key: value for key, value in cls.__dict__.items() if not key.startswith('__') and not callable(key)}

    @classmethod
    def __type_validation(cls, separator, **kwargs):
        for key, value in kwargs:
            value_type = cls.__get_attribute(key, separator)
            if not (value_type and ((type(value) is value_type)
                                    or (issubclass(value_type, Model) and type(value) is int))):
                return False
        return True

    @classmethod
    def __column_validation(cls, separator, *args):
        for column in args:
            if not cls.__get_attribute(column, separator):
                return False
        return True

    @classmethod
    def __translate_into_sql(cls, attribute):
        sql_attribute = delete_suffix(attribute).replace("__", ".")
        prefix = (cls.__name__ + '.') if '.' in attribute else ''
        return "%s%s" % (prefix, sql_attribute)

    @classmethod
    def __select(cls, arg):
        select_part = ""
        for column in arg:
            select_part += " %s," % column
        return "SELECT%s" % select_part[:-1]

    @classmethod
    def __from(cls, arg):
        join = ""
        joined = []
        need_to_join = (column_name for column_name in arg if not column_name.startswith(cls.__name__))
        for column in need_to_join:
            path = ""
            top_level_table = cls
            for path_part in column.split("."):
                path += path_part
                table = cls.__get_attribute(path, '.')
                if issubclass(table, Model) and table not in joined:
                    join += " INNER JOIN %s ON %s.entity_id = %s.%s" % (table, table, top_level_table, path_part)
                    joined.append(table)
                    top_level_table = table

        return " FROM %s%s" % (cls.__name__, join)

    @classmethod
    def __where(cls, kwargs):
        condition = ""
        formatter = " %s %s %{0}s AND".format("(%s)")
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
            condition += formatter % (attribute, operator, key)
        result = (" WHERE%s" % condition[:-4]) if condition[:-4] else ""
        return result

    @classmethod
    def insert(cls, **kwargs):
        if not cls.__type_validation("", **kwargs):
            raise ValueError

        columns = str(kwargs.keys())[1:-1]
        formatter = "%{0}s,".format("(%s)")
        insert_values = re.sub(
            r"(^[\w]+,)|( [\w]+,)|( [\w]$)",
            lambda match_obj: formatter % match_obj.group(0),
            columns
        )

        insert_values = insert_values[:-1]
        query = "INSERT INTO %s(%s) VALUES(%s)" % (cls.__name__, columns, insert_values)
        print query
        # cls.__cursor.execute(query, kwargs)
        #
        # return cls.__cursor.lastrowid

    @classmethod
    def select(cls, *args, **kwargs):
        if not (cls.__type_validation("__", **kwargs) and cls.__column_validation(".", args) and len(args) > 0):
            raise ValueError

        column_names = (cls.__translate_into_sql(column) for column in args)
        query = cls.__select(column_names) + cls.__from(column_names) + cls.__where(kwargs)
        print query
        # cls.__cursor.execute(query, kwargs)
        # TODO: return list
        # return cls.__cursor

    @classmethod
    def update(cls):
        pass

    @classmethod
    def delete(cls):
        pass
