# Simulator class to simulate stock prices of companies.
import datetime
import random

from .common import db

class StockSimulator:
    # Class variables
    names_file = "./apps/StockMarketImitation/static/text-files/company-names.json"

    # Constructor
    def __init__(self, update_intervali = None, start_date = "5/29/2012", current_date = "5/29/2012"):
        """
        Class StockSimulator provides utilities for
        simulating a number of companies in real time.
        """
        # Define instance variables
        self.start_date = start_date
        self.current_date = current_date
    

    ############ 
    # Methods
    ############
    def initialize_database(self, companies = dict()):

        """
        Empty the company and stock_history databases and fill them
        with num_companies new companies beginning at the given initial
        values with the given names and symbols.
        Prescribe default strings if names is None or symbols is None.
        """

        # Empty db
        db.company.truncate()
        db.stock_history.truncate()
        for s in companies:
            # Add company to db
            id = db.company.insert(
                company_name = companies[s]['name'],
                company_symbol = s,
                current_stock_value = companies[s]['value'],
                changes = companies[s]['change'],
            )
            # Initialize stock history
            db.stock_history.insert(
                company_id = id,
                stock_value = companies[s]['value']
            )

    def load_companies(self, id = None):
        """
        Return a dictionary of company dictionaries. The key
        for each company dictionary is the company id.
        """
        companies = {}
        if id == None:
            db_companies = db(db.company).select().as_list()
        else:
            db_companies = db(db.company.id in id).select().as_list()
        
        for c in db_companies:
            companies[c['id']] = c
        return companies
    

    def load_company_histories(self, id = None):
        """
        Return either the stock history of a given company as a list
        or a dictionary of stock history lists of each company
        If update is True, make sure stock values are up to date
        Otherwise, return history AS IS.

        Returns either a list of stock prices for the given company
        or a dictionary of lists where the keys are company ids.
        """
        
        company_histories = {}
        if id == None: 
            db_company_histories = db(db.stock_history).select().as_list()
        else: 
            db_company_histories = db(db.stock_history.id in id).select().as_list()
        for c in db_company_histories:
            company_histories[c['id']] = c
        return company_histories 
        

