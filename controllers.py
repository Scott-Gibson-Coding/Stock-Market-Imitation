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

url_signer = URLSigner(session)

@action('index')
@action.uses('index.html', db, auth)
def index():
    return {}

@action('portfolio')
@action.uses('portfolio.html', db, auth)
def portfolio():
    return {}

@action('company')
@action.uses('company.html', db, auth)
def company():
    return {}

@action('search')
@action.uses('search.html', db, auth)
def search():
    return {}

from .StockSimulator import StockSimulator
# Initialize a simulator which updates every second
Simulator = StockSimulator(1)
# Demo of chart functionality
@action('chart_demo')
@action.uses('chart_demo.html', db, url_signer)
def chart():
    # Initialize database with 5 new companies
    Simulator.initialize_database(5, [5]*5)
    return {
        'get_history_url' : URL('get_stock_history', signer=url_signer),
    }

@action('get_stock_history')
@action.uses(db, url_signer.verify())
def get_stock_history():
    # Load companies. For the demo we just use the first one.
    companies = Simulator.load_companies()
    k = list(companies.keys())[0]
    # Get the stock history of the first company (list)
    hist = Simulator.get_stock_history(k)
    return dict(
        name = companies[k]['company_name'],
        stock_history = hist,
    )
