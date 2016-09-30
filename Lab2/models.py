from __future__ import unicode_literals

import mysql.connector

from DB1_LAB2.settings import lab2_config
from django.db import models
from schema import get_tables

# Create your models here.

__tables = get_tables()
__connection = mysql.connector.connect(**lab2_config)
__cursor = __connection.cursor()


def db_change(func):
    def wrapper(table_name, **kwargs):
        global __tables
        table = __tables.get(table_name, None)
        if table:
            global __cursor
            query = func(table, **kwargs)
            __cursor.execute(query, kwargs)
    return wrapper


def get_tables_names():
    return __tables.keys()


@db_change
def add_record(table, **kwargs):
    return table.insert(kwargs)


@db_change
def update_records(table, **kwargs):
    return table.update(kwargs)


@db_change
def delete_records(table, *kwargs):
    return table.delete(kwargs)


def get_records(table_name, *args, **kwargs):
    global __tables
    table = __tables.get(table_name, None)
    if table:
        global __cursor
        query = table.select(args, kwargs)
        __cursor.execute(query, kwargs)
