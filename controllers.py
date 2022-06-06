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
from py4web.utils.form import Form, FormStyleBulma
from yatl.helpers import A
from .common import db, session, T, cache, auth, logger, authenticated, unauthenticated, flash
from py4web.utils.url_signer import URLSigner
from .models import get_user_email, get_time
from .StockSimulator import *
from .CompanyData import *

from .utilities import get_portfolio, get_avg_bought_price

url_signer = URLSigner(session)

# Get preset company data
s = StockSimulator()

# redirects user to index page if not logged in
def ensure_login():
    auth.get_user() or redirect(URL(''))

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
        init_user_url = URL('init_user'),
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

# creates new user in 'user' db if no user currently exists
# init user balance to starting balance.
init_user_starting_bal = 10000
@action('init_user')
@action.uses(db, auth)
def init_user():
    assert auth.get_user()
    current_user = auth.get_user()
    if not db(db.user.user_id == current_user['id']).select():
        id = db.user.insert(
            user_balance=init_user_starting_bal,
            user_id=current_user['id'],
        )
    return "user initialized"

@action('portfolio')
@action.uses('portfolio.html', db, auth, url_signer)
def portfolio():
    ensure_login()
    return {'get_holdings_url' : URL('get_holdings'),
            'get_user_info_url' : URL('get_user_info'),
            'update_user_profile_url' : URL('update_user_profile', signer=url_signer)}

@action('get_holdings', method='POST')
@action.uses(db, auth.user)
def get_holdings():
    user_id = auth.get_user().get('id')
    holdings = get_portfolio(user_id)['holdings']
    holdings = [{'company_name' : (c := db.company[k]).company_name, 
                 'ticker' : c.company_symbol,
                 'shares' : v,
                 'price' : c.current_stock_value,
                 'bought_price' : get_avg_bought_price(user_id, k)} for k,v in holdings.items()]
    return {'holdings' : holdings}

@action('get_user_info', method='POST')
@action.uses(db, auth.user)
def get_user_info():
    user_id = auth.get_user().get('id')
    fn = auth.get_user().get('first_name')
    ln = auth.get_user().get('last_name')
    user = db(db.user.user_id == user_id).select().first()
    return {'first_name' : fn, 'last_name' : ln, 'balance' : user.user_balance, 'pfp' : user.pfp}

@action('update_user_profile', method='POST')
@action.uses(db, auth.user, url_signer.verify())
def update_user_profile():
    fn = request.json.get('first_name')
    ln = request.json.get('last_name')
    pfp = request.json.get('pfp')
    id = auth.get_user().get('id')
    db(db.auth_user.id == id).update(first_name=fn, last_name=ln)
    db(db.user.user_id == id).update(pfp=pfp)
    return 'OK'
    


# If no ticker provided, default to S&P 500
# For now, these companies are available (go to /company/ticker):
# ^GSPC, AAPL, MSFT, AMZN, GOOGL, GOOG, TSLA, BRK.B, JNJ, UNH, FB, NVDA, XOM, JPM, PG, V, CVX, HD, MA, PFE, ABBV
@action('company')
@action('company/<ticker>')
@action.uses('company.html', db, auth)
def company(ticker='^GSPC'):
    ensure_login()
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
    ensure_login()
    return dict(search_data_url = URL('search_data'), company_url = URL('company'))

@action('search_data')
@action.uses(db, auth)
def search_data():
    company_rows = []
    simulator_data = s.load_companies()
    for key in simulator_data:
        company_rows.append(simulator_data[key])
    
    return dict(company_rows = company_rows)

# Displays categories
@action('forum')
@action.uses('forum.html', db, auth)
def forum():
    ensure_login()
    # query forum_topic db for topics in alphabetical order
    topics = db().select(db.forum_topic.ALL, orderby=db.forum_topic.topic)
    return dict(
        topics=topics
    )

@action('forum_add_topic', method=['GET', 'POST'])
@action.uses('forum_form.html', db, auth)
def forum_add_topic():
    ensure_login()
    form = Form(db.forum_topic, formstyle=FormStyleBulma)

    # handle post request from completed form
    if form.accepted:
        redirect(URL('forum'))

    # render Get request form
    return dict(
        title='Add New Forum Topic',
        form=form,
    )

# Displays posts within a category
@action('forum/<topic_id:int>')
@action.uses('forum_topic.html', db, auth)
def forum_topic(topic_id = None):
    ensure_login()
    assert topic_id is not None

    # ensure the topic id is valid
    topic = db.forum_topic[topic_id]
    assert topic != None

    # get the posts related to this topic in chronological order
    posts = db(db.forum_post.topic_id == topic_id).select(orderby=db.forum_post.post_date).as_list()
    posts.reverse()

    # go through and add the user names to each post
    for post_id in range(len(posts)):
        post = posts[post_id]
        user = db.auth_user[post['user_id']]
        if user == None:
            name = "unknown"
        else:
            name = user['first_name'] + ' ' + user['last_name']
        posts[post_id]['name'] = name

    return dict(
        topic_id=topic_id,
        topic=topic['topic'],
        posts=posts,
    )


# Displays individual post with comments
@action('forum_post/<post_id:int>')
@action.uses('forum_post.html', db, auth, url_signer)
def forum_post(post_id = None):
    ensure_login()
    assert post_id is not None
    post = db(db.forum_post.id == post_id).select().first()
    if post is None:
        redirect(URL('forum'))
    user = db.auth_user[post.user_id]
    user_name = user.first_name + " " + user.last_name
    topic = db.forum_topic[post.topic_id]
    return dict(
        url_signer=url_signer,
        post=post,
        current_user_id=auth.get_user()['id'],
        user_name=user_name,
        topic=topic,
        # Signed URLs
        get_post_url = URL('get_post', post_id),
        edit_post_url = URL('forum_edit_post', post_id, signer=url_signer),
        get_comments_url = URL('get_comments', post_id, signer=url_signer),
        save_reaction_url = URL('save_reaction', signer=url_signer),
        post_comment_url = URL('post_comment', post_id, signer=url_signer),
        delete_comment_url = URL('delete_comment', signer=url_signer),
    )

# Add a post to a forum topic
@action('forum_add_post/<topic_id:int>', method=['GET', 'POST'])
@action.uses('forum_form.html', db, auth)
def forum_add_topic(topic_id = None):
    ensure_login()
    assert topic_id != None
    topic = db.forum_topic[topic_id]
    assert topic != None

    form = Form(db.forum_post, formstyle=FormStyleBulma, dbio=False)
    # handle post request from completed form
    if form.accepted:
        db.forum_post.insert(
            topic_id=topic_id,
            post_title=form.vars['post_title'],
            post_content=form.vars['post_content']
        )
        redirect(URL('forum', topic_id))

    # render Get request form
    return dict(
        title='Add New Post in ' + topic.topic,
        form=form,
    )
    
# Edit a current post
@action('forum_edit_post/<post_id:int>', method=['POST'])
@action.uses(db, auth, url_signer.verify())
def forum_edit_post(post_id = None):
    assert post_id != None
    post = db.forum_post[post_id]
    assert post != None
    # update the forum_post db entry
    new_post_content = request.json.get('post_content')
    db(db.forum_post.id == post_id).update(post_content=new_post_content)


@action('forum_delete_post/<post_id:int>')
@action.uses(db, auth, url_signer.verify())
def forum_delete_post(post_id=None):
    assert post_id != None
    db(db.forum_post.id == post_id).delete()
    redirect(URL('forum'))


####
# Server calls from JS for the Forum
####

@action('get_post/<post_id:int>')
@action.uses(db, auth)
def get_post(post_id = None):
    assert post_id != None
    post = db.forum_post[post_id]
    assert post != None
    return dict(
        user_id=auth.get_user()['id'],
        post_author_id=post.user_id,
        post_content=post.post_content
    )


@action('get_comments/<post_id:int>')
@action.uses(db, auth, url_signer.verify())
def get_comments(post_id = None):
    assert post_id is not None
    current_user = db(db.auth_user.email == get_user_email()).select().first()
    assert current_user is not None
    # Get comments
    all_entries = db(db.forum_comment.post_id == post_id).select().as_list()
    # Add owner name and email to each comment
    # Also add the number of likers and dislikers to comments
    # Also find the replies parented to each comment
    comments = []
    reply_dict = {}
    for c in all_entries:
        user = db(db.auth_user.id == c['user_id']).select().first()
        c['user_name'] = user.first_name + " " +user.last_name
        c['user_email'] = user.email
        # Get reactions to the comment
        reactions = db(db.reaction_comment.comment_id == c['id']).select()
        # Sum likes and dislikes
        likes = 0
        dislikes = 0
        for r in reactions:
            if r.reaction == 1:
                likes += 1
            elif r.reaction == -1:
                dislikes += 1
        # Add to comment
        c['likes'] = likes
        c['dislikes'] = dislikes
        # Current user reaction
        current_reaction = db((db.reaction_comment.comment_id == c['id']) &
            (db.reaction_comment.user_id == current_user.id)).select().first()
        if current_reaction:
            c['reaction'] = current_reaction.reaction
        else:
            c['reaction'] = 0
        # If this is has a parent, add it to the reply dict
        # otherwise, it is a top level comment
        if c['parent_idx'] == -1:
            comments.append(c)
        else:
            reply_list = reply_dict.get(c['parent_idx'], [])
            reply_dict[c['parent_idx']] = reply_list + [c]
        
    # Connect the replies to the comments
    for c in comments:
        c['reply_list'] = reply_dict.get(c['id'], [])

    # Sort comments by likes-dislikes
    comments = sorted(comments, key=lambda c: c['likes']-c['dislikes'], reverse=True)
    # Return user name of the current user as well
    return dict(
        comments=comments,
        current_user_name=current_user.first_name+" "+current_user.last_name,
        current_user_email = get_user_email(),
    )

@action('save_reaction', method="POST")
@action.uses(db, auth, url_signer.verify())
def save_reaction():
    comment_id = request.json.get('comment_id')
    reaction = request.json.get('reaction')
    user = db(db.auth_user.email == get_user_email()).select().first()
    # Check whether the comment has been deleted
    comment = db(db.forum_comment.id == comment_id).select().first()
    if comment is None:
        return "Save Failed, Comment Not Found."
    # else: Insert or update the reaction
    db.reaction_comment.update_or_insert(
        ((db.reaction_comment.comment_id == comment_id) & 
        (db.reaction_comment.user_id == user.id)),
        comment_id = comment_id,
        user_id = user.id,
        reaction = reaction,
    )
    return "ok"

@action('post_comment/<post_id:int>', method="POST")
@action.uses(db, auth, url_signer.verify())
def post_comment(post_id = None):
    assert post_id is not None
    comment_text = request.json.get("comment_text")
    parent_idx = request.json.get('parent_idx')
    user = db(db.auth_user.email == get_user_email()).select().first()
    assert user is not None
    user_name = user.first_name + " " + user.last_name
    # Check that the parent comment still exists if not a top level comment
    if parent_idx != -1:
        parent = db(db.forum_comment.id == parent_idx).select().first()
        if parent is None:
            return dict(
                user_name = user_name,
                user_email = get_user_email(),
                note="Post Failed, Parent Not Found",
            )
    id = db.forum_comment.insert(
        user_id = user.id,
        post_id = post_id,
        parent_idx = parent_idx,
        comment=comment_text,
    )
    date = db(db.forum_comment.id == id).select().first().comment_date
    return dict(
        id = id,
        post_id = post_id,
        parent_idx=parent_idx,
        comment_date = date,
        user_id = user.id,
        user_name = user_name,
        user_email = get_user_email(),
    )

@action('delete_comment')
@action.uses(db, auth, url_signer.verify())
def delete_comment():
    comment_id = request.params.get('comment_id')
    comment = db(db.forum_comment.id == comment_id).select().first()
    if comment is None:
        return "Delete Failed, Post Not Found."
    owner = db(db.auth_user.id == comment.user_id).select().first()
    # Check that the owner is the one trying to delete this post.
    if owner.email != get_user_email():
        return "Delete Failed, Owner does not match."
    #else the current user owns the post, so delete it
    # If the post is a top level post (not a reply), we
    # need to delete the replies linked to it as well
    if comment.parent_idx == -1:
        db(db.forum_comment.parent_idx == comment.id).delete()
    db(db.forum_comment.id == comment_id).delete()
    return "ok"
