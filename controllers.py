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
from .CompanyData import *

url_signer = URLSigner(session)

# Get preset company data
s = StockSimulator()


@action('load_db')
@action.uses(db)
def load_db():
    s.initialize_database(preset_companies())
load_db()


@action('index')
@action.uses('index.html', auth)
def index():
    user = auth.get_user()
    return dict(
        user=user,
        login_url = URL('auth/api/login'),
        signup_url = URL('auth/api/register'),
        verify_email_url = URL('verify_email'),
    )




# returns True if the email is already in the auth_user table
@action('verify_email')
@action.uses(db)
def verify_email():
    email = request.params.get('email')
    user = db(db.auth_user.email == email).select().first()
    return dict(
        exists = (user != None),
    )


@action('portfolio')
@action.uses('portfolio.html', db, auth)
def portfolio():
    return {}


# If no ticker provided, default to S&P 500
# For now, these companies are available (go to /company/ticker):
# ^GSPC, AAPL, MSFT, AMZN, GOOGL, GOOG, TSLA, BRK.B, JNJ, UNH, FB, NVDA, XOM, JPM, PG, V, CVX, HD, MA, PFE, ABBV
@action('company')
@action('company/<ticker>')
@action.uses('company.html', db, auth)
def company(ticker='^GSPC'):
    # TODO temporarily initailizing here since db locks when initializing outside of a page function
    #   sqlite3.OperationalError: database is locked
    # If invalid ticker, simply redirect to default company page
 
    return load_company_data(ticker)

@action('company_refresh', method="POST")
@action.uses(db, auth)
def company_refresh():
    ticker = request.json.get('co_ticker')
    
    return load_company_data(ticker)


@action('load_company', method="POST")
@action.uses(db)
def load_company():
    ticker = request.json.get('co_ticker')
    # Get company info from db
    return load_company_data(ticker)


def load_company_data(ticker):

    my_company = s.load_company(ticker)
    # If invalid ticker, simply redirect to default company page
    co_id = my_company['id']
    co_name = my_company['company_name']
    co_ticker = ticker
    co_price = my_company['current_stock_value']
    co_change = my_company['changes'] 
    co_pct_change = round((co_change / co_price) * 100, 2)
    current_date = my_company['latest_update'].strftime("%m/%d/%Y, %H:%M:%S") 
    return dict(
        co_id=co_id,
        co_name=co_name,
        co_ticker=co_ticker,
        co_price=co_price,
        co_change=co_change,
        co_pct_change=co_pct_change,
        date=current_date,
        company_refresh_url=URL('company_refresh'),
        get_history_url=URL('get_stock_history'),
        load_company_url=URL('load_company'),
    )

@action('get_stock_history', method="POST")
@action.uses(db)
def get_stock_history():
    import datetime
    # Load given company
    co_ticker = request.json.get('co_ticker')
    co_name = request.json.get('co_name')
    # Get stock history
    hist = []
    times = []
    #We will do 20 steps from start up time to current time by defaulti
    steps = 200
    duration = (s.current_time - s.start_time).total_seconds()
    for i in range(steps + 1):
        times.append(s.start_time + datetime.timedelta(seconds = i * duration // steps))
    for t in times:
        co = s.load_company(co_ticker, t)
        hist.append(co['current_stock_value'])
    return dict(
        name=co_name,
        stock_history=hist,
        dates=times,
    )


@action('search')
@action.uses('search.html', db, auth)
def search():
    return dict(search_data_url = URL('search_data'), company_url = URL('company'))


@action('search_data')
@action.uses(db, auth)
def search_data():
    company_rows = []
    simulator_data = s.load_companies()
    for key in simulator_data:
        company_rows.append(simulator_data[key])
    
    return dict(company_rows = company_rows)

