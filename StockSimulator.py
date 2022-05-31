# Simulator class to simulate stock prices of companies.
import datetime
from pytz import timezone
import random
import math
from .common import db


class StockSimulator:
    # Class variables
    names_file = "./apps/StockMarketImitation/static/text-files/company-names.json"

    # Constructor
    def __init__(self, update_intervali = None):
        """
        Class StockSimulator provides utilities for
        simulating a number of companies in real time.
        """
        # Define instance variables
        self.start_time = self.get_time()
        self.current_time = self.get_time()
    



    ############ 
    # Methods
    ############
    
    
    def initialize_database(self, companies = dict()):

        """
        Empty the company and stock_history databases and fill them
        with num_companies new companies beginning at the given initial
        values with the given names and symbols.
        Prescribe default strings if names is None or symbols is None.
        TODO stock history is not used right now and needs to be removed. 
        """

        # Empty db
        db.company.truncate()
        for s in companies:
            # Add company to db
            id = db.company.insert(
                company_name = companies[s]['name'],
                company_symbol = s,
                current_stock_value = companies[s]['value'],
                changes = companies[s]['change'],
            )

    def load_companies(self, current_time = None):
        """
        Return a dictionary of company dictionaries. The key
        for each company dictionary is the company id.
        
        Before returning, the stocka are updated with the current value
        TODO, the key should  probably be the symbol instead. 
        """
        self.update_current_time()
        companies = {}
        db_companies = db(db.company).select().as_list()

        for c in db_companies:
            companies[c['id']] = c
        for c in companies: 
            companies[c]['current_stock_value'] = companies[c]['current_stock_value'] * self.change_function(current_time) 
            companies[c]['changes'] = companies[c]['current_stock_value'] * (self.change_function(current_time) - 1)
            companies[c]['latest_update'] = self.current_time
        return companies

    def load_company(self, symbol, current_time = None):
        assert(symbol != None)

        self.update_current_time()
        company = db(db.company.company_symbol == symbol).select().as_list()[0]
        company['current_stock_value'] = company['current_stock_value'] * self.change_function(current_time) 
        company['changes'] = company['current_stock_value'] * (self.change_function(current_time) - 1)
        company['latest_update'] = self.current_time
        return company


    def update_current_time(self): 
        """
        This will update the current_time field in the simulator with the EST current time. 
        """
        self.current_time = self.get_time()

    def change_function(self, current_time = None):
        """
        Deterministic noise for the stocks returns a value ~1.  
        """
        if current_time == None:
            current_time = self.current_time
        time_diff = (current_time - self.start_time).total_seconds()
        #base growth 7% per hour
        
        #change = math.pow(1.07, time_diff / 3600)
        change = 1
        #noise
        change = change + 0.001 * ( math.sin(time_diff) + math.sin(time_diff /5) + math.sin(time_diff / 24))
        return change

    def get_time(self):
        """
        Returns a dateime object for the current time in New York.
        """
        now = timezone('UTC').localize(datetime.datetime.utcnow())
        nyc = timezone('America/New_York')
        return now.astimezone(nyc)

