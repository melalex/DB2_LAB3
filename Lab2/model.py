import re
import mysql.connector

from DB1_LAB2.settings import lab2_config


def delete_extra(path):
    result = path
    if path.endswith("__lt") or \
            path.endswith("__le") or \
            path.endswith("__gt") or \
            path.endswith("__ge") or \
            path.endswith("__ne"):
        result = path[:-4]

    if path.startswith("where__"):
        result = path[7:]

    return result


def delete_suffix_decorator(class_method):
    def wrapper(cls, path, separator):
        attribute = delete_extra(path)
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
    def __type_validation(cls, separator, kwargs):
        for key, value in kwargs:
            value_type = cls.__get_attribute(key, separator)
            if not (value_type and ((type(value) is value_type)
                                    or (issubclass(value_type, Model) and type(value) is int))):
                return False
        return True

    @classmethod
    def __column_validation(cls, separator, args):
        for column in args:
            if not cls.__get_attribute(column, separator):
                return False
        return True

    @classmethod
    def __translate_into_sql(cls, attribute):
        sql_attribute = delete_extra(attribute).replace("__", ".")
        prefix = (cls.__name__ + '.') if '.' in attribute else ''
        return prefix + sql_attribute

    @classmethod
    def __set_correct_prefix(cls, attribute):
        result = attribute
        if not attribute.startswith(cls.__name__):
            path = ""
            top_level_table = cls
            for path_part in attribute.split("."):
                path += path_part
                table = cls.__get_attribute(path, '.')
                if issubclass(table, Model):
                    top_level_table = table
                    path += '.'
                else:
                    result = top_level_table.__name__ + '.' + path_part
        return result

    @classmethod
    def __select(cls, arg):
        select_part = ""
        for column in arg:
            attribute = cls.__set_correct_prefix(column)
            select_part += (attribute + ", ")
        return "SELECT%s FROM " % select_part[:-2]

    @classmethod
    def __used_tables(cls, arg):
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
                    path += '.'

        return cls.__name__ + join

    @classmethod
    def __set(cls, to_set):
        expression = ""
        formatter = "%s = %{0}s, ".format("(%s)")
        for column in to_set:
            attribute = cls.__set_correct_prefix(cls.__translate_into_sql(column))
            expression += formatter % (attribute, column)
        return "SET %s" % expression[:-2]

    @classmethod
    def __where(cls, keys):
        condition = ""
        formatter = " %s %s %{0}s AND".format("(%s)")
        for key in keys:
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
            attribute = cls.__set_correct_prefix(attribute)
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
        if not (cls.__type_validation("__", kwargs) and cls.__column_validation(".", args) and len(args) > 0):
            raise ValueError

        column_names = (cls.__translate_into_sql(column) for column in args)
        query = cls.__select(column_names) + cls.__used_tables(column_names) + cls.__where(kwargs.keys())
        print query
        # cls.__cursor.execute(query, kwargs)
        # TODO: return list
        # return cls.__cursor

    @classmethod
    def update(cls, **kwargs):
        if not cls.__type_validation("__", kwargs):
            raise ValueError

        keys = kwargs.keys()
        column_names = (cls.__translate_into_sql(column) for column in keys)
        set_list = (attribute for attribute in keys if not attribute.startswith("where__"))
        where_list = (attribute for attribute in keys if attribute.startswith("where__"))
        query = "UPDATE " + cls.__used_tables(column_names) + cls.__set(set_list) + cls.__where(where_list)
        print query

    @classmethod
    def delete(cls, **kwargs):
        if not cls.__type_validation("__", kwargs):
            raise ValueError

        keys = kwargs.keys()
        column_names = (cls.__translate_into_sql(column) for column in keys)
        query = "DELETE %s.* FROM %s WHERE %s" % (cls.__name__, cls.__used_tables(column_names), cls.__where(keys))
        print query
