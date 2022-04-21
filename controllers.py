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

from py4web import URL, abort, action, redirect, request
from py4web.utils.url_signer import URLSigner
from yatl.helpers import A

from .common import (T, auth, authenticated, cache, db, flash, logger, session,
                     unauthenticated)
from .models import get_user_email

url_signer = URLSigner(session)

@action('index')
@action.uses(db, auth, 'index.html')
def index():
    print("User:", get_user_email())
    return globals()

@action('profile')
@action.uses(db, auth,'profile.html')
def profile():
    print(globals()['auth'].get_user())
    return globals()
    
@action('company')
@action.uses(db, auth, 'company.html')
def company():
    print(globals()['auth'].get_user())
    return globals()

@action('search')
@action.uses(db, auth, 'search.html')
def search():
    print(globals()['auth'].get_user())
    return globals()
