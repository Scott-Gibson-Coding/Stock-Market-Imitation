"""
Here we can put functions which are imported and used by controllers.py
This way we don't have to clutter the controllers.py file with function
declarations that are unrelated to hooking pages to URLs
"""
from .common import db

# Function to get user balance, might be useful when computing the total
# value of the user's holdings using functions similar to ones below.
def get_user_balance(user_id = None):
    """
    Get the balance of the user from the database
    """
    assert user_id is not None
    user = db(db.user.id == user_id).select().first()
    if user is None:
        return None
    return user.user_balance

# Function to compute the current stock holdings of a user
# REQUIRES: user_id
def compute_current_holdings(user_id=None):
    """
    Compute the current value of all stocks a user owns, but has not
    yet sold.
    Returns a dictionary of company id, holding value pairs
    as well as the total value of all stocks currently owned under the 'total' key
    Note: Does not compute earnings, just the raw value of the stocks
    """
    assert user_id is not None
    # Get the transactions which belong to this user
    # Specify the user table as well so that you get the user details
    rows = db(
        (db.transaction.user_id == user_id) &
        (db.user.id == user_id)
    ).select()
    # Initialize a holdings dictionary, then loop through the rows
    # and compute the current holdings of this user for each company.
    company_holdings = {}
    for r in rows:
        # If the stock hasn't been sold yet, add its current value
        if r.stock_sell_date == "N/A":
            # For this, we need the current value
            company = db(db.company.id == r.transaction.company_id).select().first()
            # Update the value in the dictionary at the current company id
            company_holdings[company.id] = company_holdings.get(company.id, 0) + (r.transaction.stock_count * company.current_stock_value)
    # Add total field to dictionary
    total_holdings = 0
    for value in company_holdings.values():
        total_holdings += value
    company_holdings['total'] = total_holdings
    return company_holdings

        

# Function to compute the current stock value of a user
# REQUIRES: user_id
def compute_current_profit(user_id=None):
    """
    Compute the current earnings on all stocks a user owns, but has not
    yet sold.
    Returns a dictionary of company id, stock earning pairs
    as well as the total earnings over all stocks currently held at the 'total' key
    """
    assert user_id is not None
    # Get the transactions which belong to this user
    # Specify the user table as well so that you get the user details
    rows = db(
        (db.transaction.user_id == user_id) &
        (db.user.id == user_id)
    ).select()
    # Initialize a profit dictionary, then loop through the rows
    # and compute the current holdings of this user.
    company_profit = {}
    for r in rows:
        # If the stock hasn't been sold yet, add it's value
        if r.stock_sell_date == "N/A":
            # For this, we need the current value
            company = db(db.company.id == r.transaction.company_id).select().first()
            # How much has the price changed since purchase?
            stock_delta = company.current_stock_value - r.transaction.stock_buy_value
            # Add this amount times the number of stocks to the total profit from
            # the current company
            company_profit[company.id] = company_profit.get(company.id, 0) + (stock_delta * r.transaction.stock_count)
    # Compute total profit from all stocks currently held and add as another field
    total_profit = 0
    for value in company_profit.values():
        total_profit += value
    company_profit['total'] = total_profit
    return company_profit

# Function to compute the total profit from all stocks sold previously
# REQUIRES: user_id
def compute_historical_profit(user_id=None):
    """
    Compute the earnings from all stocks a user sold previously
    Returns a dictionary of company id, stock earning pairs
    as well as the total earnings over all stocks at the 'total' key
    """
    assert user_id is not None
    # Get the transactions which belong to this user
    # Specify the user table as well so that you get the user details
    rows = db(
        (db.transaction.user_id == user_id) &
        (db.user.id == user_id)
    ).select()
    # Initialize a profit dictionary, then loop through the rows
    # and compute the historical earnings of this user.
    company_profit = {}
    for r in rows:
        # Stock must have been sold previously
        if r.stock_sell_date != "N/A":
            earnings = r.transaction.stock_count * (r.transaction.stock_sell_value - r.transaction.stock_buy_value)
            company_profit[r.transaction.company_id] = company_profit.get(r.transaction.company_id, 0) + earnings
    # Compute total profit from all stocks sold and add as total value
    total_profit = 0
    for value in company_profit.values():
        total_profit += value
    company_profit['total'] = total_profit
    return company_profit