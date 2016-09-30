from datetime import datetime


class SqlDate(object):
    @classmethod
    def type_check(cls, value):
        result = True
        try:
            datetime.strptime(value, '%Y-%m-%d')
        except ValueError:
            result = False
        return result


class SqlEnum(object):
    def __init__(self, args):
        self.possible_values = args

    def type_check(self, value):
        result = False
        if value in self.possible_values:
            result = True
        return result


def is_sql_type(value_type, value):
    result = False
    if (value_type is SqlDate) or isinstance(value_type, SqlEnum):
        result = value_type.type_check(value)
    return result
