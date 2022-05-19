# Simulator class to simulate stock prices of companies.
import datetime
import random

class Company:
    """
    Company class basically just holds information about a company
    for testing purposes.
    Will be replaced by db stuff later.
    """
    # Class variables

    # Constructor
    def __init__(self, name, initial_price, latest_update):
        self.name = name
        self.stock_price = [initial_price]
        self.latest_update = latest_update
    
    ##########
    # Methods
    ##########

    def __str__(self):
        rep = {
            'name' : self.name,
            'stock_price' : self.stock_price,
            'latest_update' : self.latest_update,
        }
        return str(rep)
    __repr__ = __str__


class StockSimulator:
    # Class variables
    
    # Constructor
    def __init__(self, num_companies, initial_values, 
                update_interval):
        assert num_companies == len(initial_values), "Number of companies must equal the number of initial values prescribed."        
        # Define instance variables
        self.num_companies = num_companies
        current_time = datetime.datetime.utcnow()
        self.update_interval = update_interval
        self.companies = self.generate_companies(num_companies, initial_values, current_time)
    
    ############ 
    # Methods
    ############

    # Generate the company names
    # For now, just give them generic names and symbols
    def generate_companies(self, num_companies, initial_values, current_time):
        companies = {}
        for i in range(num_companies):
            name = "c" + str(i)
            val = initial_values[i]
            c = Company(name, val, current_time)
            # Add company into dictionary with symbol same as name
            companies[name] = c
        return companies

    def generate_new_values(self, values, n):
        """
        Generate n new values and return the new values generated
        For now, just do a simple random walk based on last value
        """
        new_vals = [0]*n
        for i in range(n):
            if i == 0:
                new_vals[i] = values[-1] + random.random()-0.5
            else:
                new_vals[i] = new_vals[i-1] + random.random()-0.5 
        return new_vals
    
    def check_for_updates(self, symbol=None):
        """
        Check whether the stock value for the given company
        is current. If not, get new values for the stock
        """
        assert symbol is not None
        c = self.companies.get(symbol, None)
        if c is None:
            raise ValueError("Company with symbol \"{}\" does not exist.".format(symbol))
        current_time = datetime.datetime.utcnow()
        time_delta = (current_time-c.latest_update).seconds
        if time_delta >= self.update_interval:
            # We need to generate at least one new value
            n = int(time_delta / self.update_interval)
            c.stock_price += self.generate_new_values(c.stock_price, n)
            c.latest_update = current_time

    def get_stock_history(self, symbol=None, update=True):
        """
        Return either the stock history of a given company as a list
        or a dictionary of stock history lists of each company
        If update is True, make sure stock values are up to date
        Otherwise, return history AS IS.
        """
        if symbol is None:
            # Get history for every company
            stock_prices = {}
            for k in self.companies.keys():
                if update:
                    self.check_for_updates(k)
                stock_prices[k] = self.companies[k].stock_price
            return stock_prices
        #else we have a specific company
        c = self.companies.get(symbol, None)
        if c is None:
            raise ValueError("Company with symbol \"{}\" does not exist.".format(symbol))
        if update:
            self.check_for_updates(symbol)
        hist = c.stock_price
        return hist
    
    def get_current_value(self, symbol=None, update=True):
        """
        Return either the current stock value of the given company or
        the current values of every company.
        If update is True, make sure stock value is up to date.
        Otherwise, return current value(s) AS IS.
        """
        companies_to_query = []
        if symbol is None:
            companies_to_query = [s for s in self.companies.keys()]
        else:
            companies_to_query = [symbol]
        # For each company, make sure they have the latest value
        if update:
            for symb in companies_to_query:
                self.check_for_updates(symb)
        if len(companies_to_query) == 1:
            return self.companies[companies_to_query[0]].stock_price[-1]
        return {
            s:self.companies[s].stock_price[-1] for s in companies_to_query
        }
