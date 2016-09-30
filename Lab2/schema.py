from sql_types import SqlDate
from sql_types import SqlEnum
from model import Model


class Customers(Model):
    first_name = str
    last_name = str
    address = str
    birthday = SqlDate
    vip_flg = bool


class Offices(Model):
    name = str
    address = str


class Employees(Model):
    first_name = str
    last_name = str
    start_date = SqlDate
    end_date = SqlDate


class Products(Model):
    short_desc = str
    long_desc = str
    valid_from = SqlDate
    valid_to = SqlDate


class Account(Model):
    product_id = Products
    emp_id = Employees
    office_id = Offices
    customer_id = Customers
    open_date = SqlDate
    close_date = SqlDate
    status = SqlEnum("opened, closed, frozen")
    balance = float
