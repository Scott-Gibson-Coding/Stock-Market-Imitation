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
db.define_table(
    'transaction',
    Field('company_id', 'reference company'), # The company whose stock this is
    Field('user_id', 'reference user'), # The owner of this transaction
    Field('transaction_type', requires=IS_IN_SET(['buy', 'sell'])),
    Field('count', type='float', requires=IS_FLOAT_IN_RANGE(0, None)),
    Field('value_per_share', type='float', requires=IS_FLOAT_IN_RANGE(0, None)),
    Field('transaction_date', 'datetime', default=get_time)
)

# Table to hold the forum topics
db.define_table(
    'forum_topic',
    Field('topic', requires=IS_NOT_EMPTY()),
)

# Table to hold forum posts
db.define_table(
    'forum_post',
    Field('user_id', 'reference auth_user'),
    Field('topic_id', 'reference forum_topic'),
    Field('post_title', requires=IS_NOT_EMPTY()),
    Field('post_content', requires=IS_NOT_EMPTY()),
    Field('post_date', 'datetime', default=get_time)
)

# Table to hold forum post comments
db.define_table(
    'forum_comment',
    Field('user_id', 'reference auth_user'),
    Field('post_id', 'reference forum_post'),
    Field('parent_idx', 'integer', default=-1), # Not a reference since it can be empty
    Field('comment', requires=IS_NOT_EMPTY()),
    Field('comment_date', 'datetime', default=get_time)
)

# Table to hold reactions to comments
db.define_table(
    'reaction_comment',
    Field('comment_id', 'reference forum_comment'),
    Field('user_id', 'reference auth_user'),
    Field('reaction', 'integer', default=0),
)

# Reactions to posts?


# TODO: Make fields unreadable and unwritable if they would appear in forms...


db.commit()
