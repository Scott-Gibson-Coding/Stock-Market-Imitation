"""
This file defines the database models
"""

import datetime
from .common import db, Field, auth
from pydal.validators import *


def get_user_email():
    return auth.current_user.get('email') if auth.current_user else None

def get_time():
    return datetime.datetime.utcnow()


### Define your table below
#
# db.define_table('thing', Field('name'))
#
## always commit your models to avoid problems later

# auth.current_user already holds email, first name, and last name
# but we still need to save the amount of money a user has
# available for investing.
# User table, could be used for user balance, nickname, profile details, profile image,...
db.define_table(
    'user',
    Field('user_balance', 'float', default=0.),
    Field('user_email', default=get_user_email),
)

# Company table for information about companies
# This might be implemented another way depending on how we
# get stock information / history
db.define_table(
    'company',
    Field('company_name'),
    Field('company_symbol'),
    Field('current_stock_value', 'float', default=0.),
    Field('latest_update', 'datetime', default=get_time),
)

# Stock history table to keep track of the history
# of each company. The id of the entries in the table
# should provide the order in which the values were generated.
db.define_table(
    'stock_history',
    Field('company_id', 'reference company'),
    Field('stock_value', 'float'),
)

# Transaction table to hold info about all the transactions taking place
# We can see what a user owns by iterating through transactions and noting
# what they currently have and what they used to have.
# I.e. if stock_sell_date has a value or a date before the current date, depending
# on how we define it.
# Since stock_sell_value and stock_sell_date are initially empty, we should have a convention
# which can be noticed.
db.define_table(
    'transaction',
    Field('company_id', 'reference company'), # The company whose stock this is
    Field('user_id', 'reference user'), # The owner of this transaction
    Field('transaction_type', requires=IS_IN_SET(['buy', 'sell'])),
    Field('count', type='float', requires=IS_FLOAT_IN_RANGE(0, None)),
    Field('value_per_share', type='float', requires=IS_FLOAT_IN_RANGE(0, None)),
    Field('transaction_date', 'datetime', default=get_time)
)

# TODO: Make fields unreadable and unwritable if they would appear in forms...


db.commit()
