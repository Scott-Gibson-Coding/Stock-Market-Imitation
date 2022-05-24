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
my_companies = preset_companies()
my_company_values = list(my_companies['values'].values())
my_company_names = list(my_companies['companies'].values())
my_company_tickers = list(my_companies['companies'].keys())
my_company_changes = my_companies['changes']

# Initialize StockSimulator to update every 1 second
s = StockSimulator(1)


@action('index')
@action.uses('index.html', auth)
def index():
    user = auth.get_user()
    return dict(
        user=user,
        login_url = URL('auth/api/login'),
        sign_up_url = URL('auth/api/register'),
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
