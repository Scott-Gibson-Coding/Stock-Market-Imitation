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
from .StockSimulator import *

from .utilities import get_portfolio, get_avg_bought_price

url_signer = URLSigner(session)


# Using top 20 S&P 500 companies for now while testing
# https://www.slickcharts.com/sp500
def preset_companies():
    return dict(
        companies={
            '^GSPC': 'S&P 500', 'AAPL': 'Apple Inc.', 'MSFT': 'Microsoft Corporation', 'AMZN': 'Amazon.com Inc.',
            'GOOGL': 'Alphabet Inc. Class A', 'GOOG': 'Alphabet Inc. Class C', 'TSLA': 'Tesla Inc',
            'BRK.B': 'Berkshire Hathaway Inc. Class B', 'JNJ': 'Johnson & Johnson',
            'UNH': 'UnitedHealth Group Incorporated', 'FB': 'Meta Platforms Inc. Class A', 'NVDA': 'NVIDIA Corporation',
            'XOM': 'Exxon Mobil Corporation', 'JPM': 'JPMorgan Chase & Co.', 'PG': 'Procter & Gamble Company',
            'V': 'Visa Inc. Class A', 'CVX': 'Chevron Corporation', 'HD': 'Home Depot Inc.',
            'MA': 'Mastercard Incorporated Class A', 'PFE': 'Pfizer Inc.', 'ABBV': 'AbbVie Inc.',
        },
        values={
            '^GSPC': 3901.36, 'AAPL': 137.60, 'MSFT': 252.94, 'AMZN': 2159.37, 'GOOGL': 2180.08, 'GOOG': 2187.00,
            'TSLA': 665.40, 'BRK.B': 304.05, 'JNJ': 177.25, 'UNH': 485.73, 'FB': 193.81, 'NVDA': 166.94, 'XOM': 92.25,
            'JPM': 117.37, 'PG': 141.88, 'V': 200.00, 'CVX': 168.50, 'HD': 287.80, 'MA': 336.00, 'PFE': 52.51,
            'ABBV': 151.01,
        },
        changes={
            '^GSPC': 0.57, 'AAPL': 0.01, 'MSFT': 0.38, 'AMZN': 7.55, 'GOOGL': 1.92, 'GOOG': 0.74, 'TSLA': 1.50,
            'BRK.B': 0.00, 'JNJ': 0.27, 'UNH': 0.00, 'FB': 0.27, 'NVDA': 0.00, 'XOM': 0.39, 'JPM': 0.03,
            'PG': 0.09, 'V': 0.97, 'CVX': 0.68, 'HD': 0.61, 'MA': -0.18, 'PFE': 0.04, 'ABBV': 0.00,
        }
    )


my_companies = preset_companies()
my_company_values = list(my_companies['values'].values())
my_company_names = list(my_companies['companies'].values())
my_company_tickers = list(my_companies['companies'].keys())
my_company_changes = my_companies['changes']


s = StockSimulator(1)  # update every 1 sec


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


# If no ticker provided, default to S&P 500
# For now, these companies are available (go to /company/ticker):
# ^GSPC, AAPL, MSFT, AMZN, GOOGL, GOOG, TSLA, BRK.B, JNJ, UNH, FB, NVDA, XOM, JPM, PG, V, CVX, HD, MA, PFE, ABBV
@action('company')
@action('company/<ticker>')
@action.uses('company.html', db, auth)
def company(ticker='^GSPC'):
    # TODO temporarily initailizing here since db locks when initializing outside of a page function
    #   sqlite3.OperationalError: database is locked
    s.initialize_database(
        21,                 # Number of companies
        my_company_values,  # Initial values
        my_company_names,   # Company names
        my_company_tickers  # Company tickers
    )
    companies = s.load_companies()
    # .
    my_company = None
    for c in companies.values():
        if c['company_symbol'] == ticker:
            my_company = c
    # If invalid ticker, simply redirect to default company page
    if not my_company:
        redirect(URL('company'))
    co_id = my_company['id']
    co_name = my_company['company_name']
    co_ticker = ticker
    co_price = my_company['current_stock_value']
    co_change = my_company_changes[ticker]  # TODO should we also store this in db or compute it?
    co_pct_change = round((co_change / co_price) * 100, 2)
    current_date = my_company['latest_update'].strftime("%m/%d/%Y, %H:%M:%S")  # TODO Should use US Eastern time in simulator
    return dict(
        co_id=co_id,
        co_name=co_name,
        co_ticker=co_ticker,
        co_price=co_price,
        co_change=co_change,
        co_pct_change=co_pct_change,
        date=current_date,
        company_refresh_url=URL('company_refresh'),
    )


@action('company_refresh', method="POST")
@action.uses(db, auth)
def company_refresh():
    co_id = request.json.get('co_id')
    s.check_for_updates(co_id)
    # TODO cannot change co_change or co_pct_change in simulator, and not saved in db
    #   Will need to use historical data to calculate change based on the user's selected time period
    updated_companies = s.load_companies()
    my_company = updated_companies[co_id]
    return dict(companies=my_company)


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
