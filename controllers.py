"""
This file defines actions, i.e. functions the URLs are mapped into
The @action(path) decorator exposed the function at URL:

    http://127.0.0.1:8000/{app_name}/{path}

If app_name == '_default' then simply

    http://127.0.0.1:8000/{path}

If path == 'index' it can be omitted:

    http://127.0.0.1:8000/

The path follows the bottlepy syntax.

@action.uses('generic.html')  indicates that the action uses the generic.html template
@action.uses(session)         indicates that the action uses the session
@action.uses(db)              indicates that the action uses the db
@action.uses(T)               indicates that the action uses the i18n & pluralization
@action.uses(auth.user)       indicates that the action requires a logged in user
@action.uses(auth)            indicates that the action requires the auth object

session, db, T, auth, and tempates are examples of Fixtures.
Warning: Fixtures MUST be declared with @action.uses({fixtures}) else your app will result in undefined behavior
"""

from py4web import action, request, abort, redirect, URL
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email

from .utilities import get_portfolio, get_avg_bought_price

url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', db, auth)
def index():
    return {}

@action('portfolio')
@action.uses('portfolio.html', db, auth)
def portfolio():
    return {'get_holdings_url' : URL('get_holdings')}

@action('get_holdings', method='POST')
@action.uses(db, auth.user)
def get_holdings():
    user_id = auth.get_user().get('id')
    holdings = get_portfolio(user_id)['holdings']
    holdings = [{'company_name' : db.company[k].company_name, 
                 'shares' : v,
                 'price' : db.company[k].current_stock_value,
                 'bought_price' : get_avg_bought_price(user_id, k)} for k,v in holdings.items()]
    return {'holdings' : holdings}

@action('company')
@action.uses('company.html', db, auth)
def company():
    return {}

@action('search')
@action.uses('search.html', db, auth)
def search():
    return {}

@action('test_setup')
@action.uses(db, auth.user)
def test_setup():
    db.company.truncate()
    db.transaction.truncate()
    db.user.truncate()
    user_id = db.user.insert()

    a = db.company.insert(company_name='AAA', company_symbol='A', current_stock_value=10)
    b = db.company.insert(company_name='BBB', company_symbol='B', current_stock_value=50)
    c = db.company.insert(company_name='CCC', company_symbol='C', current_stock_value=100)
    d = db.company.insert(company_name='DDD', company_symbol='D', current_stock_value=500)

    db.transaction.insert(company_id=a, 
                          user_id=user_id, 
                          transaction_type='buy', 
                          count=5, 
                          value_per_share=10)
    
    db.transaction.insert(company_id=b, 
                          user_id=user_id, 
                          transaction_type='buy', 
                          count=6, 
                          value_per_share=50)
    db.transaction.insert(company_id=c, 
                          user_id=user_id, 
                          transaction_type='buy', 
                          count=7, 
                          value_per_share=100)
    db.transaction.insert(company_id=d, 
                          user_id=user_id, 
                          transaction_type='buy', 
                          count=8, 
                          value_per_share=500)
    return 'OK'
