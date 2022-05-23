# Simulator class to simulate stock prices of companies.
import datetime
import random

from .common import db

class StockSimulator:
    # Class variables
    names_file = "./apps/StockMarketImitation/static/text-files/company-names.json"

    # Constructor
    def __init__(self, update_interval):
        """
        Class StockSimulator provides utilities for
        simulating a number of companies in real time.

        Params:
        update_interval : The number of seconds between updates
        to the stock value of each company.
        """
        # Define instance variables
        self.update_interval = update_interval
    
    ####
    # Getters / Setters
    ####
    def get_stock_price(self, company_id):
        hist = db(db.stock_history.company_id == company_id).select()
        stock_hist = [s.stock_value for s in hist]
        return stock_hist
    
    def get_latest_update_time(self, company_id):
        date = db(db.company.id == company_id).select().first().latest_update
        return date

    def append_stock_price(self, company_id, new_vals):
        # Insert the new stock values into the db
        for val in new_vals:
            db.stock_history.insert(company_id = company_id, stock_value=val)
    
    def set_current_value(self, company_id, value, time):
        db(db.company.id == company_id).update(
            current_stock_value=value,
            latest_update=time,
        )

    ############ 
    # Methods
    ############

    def create_company_names(self, n):
        """
        If the names are not provided, creation of company names will be
        done in this function. Accesses names and suffixes from the names file
        class variable.
        
        Params:
        n : The number of companies to generate
        Returns: A list of company names.
        """
        import json
        names = []
        with open(self.names_file, 'r') as json_file:
            name_file = json.load(json_file)
            name_list = name_file['name_string'].split(' ')
            suffixes = name_file['suffixes']
            n_possible = len(name_list)*len(suffixes)
            for i in range(n):
                name = random.choice(name_list)
                sfx = random.choice(suffixes)
                new_name = (name + " " + sfx).strip(" ")
                if (n_possible > 2*n) and (new_name in names):
                    i -= 1
                    continue
                names.append(new_name)
        return names

    def initialize_database(self, num_companies, initial_values, names=None, symbols=None):
        """
        Empty the company and stock_history databases and fill them
        with num_companies new companies beginning at the given initial
        values with the given names and symbols.
        Prescribe default strings if names is None or symbols is None.
        """
        assert num_companies == len(initial_values), "The number of companies must equal the number of prescribed initial stock prices."
        if names is None:
            #names = ["c"+str(i) for i in range(num_companies)]
            names = self.create_company_names(num_companies)
        if symbols is None:
            symbols = ["c"+str(i) for i in range(num_companies)]
        assert len(names) == num_companies, "The number of companies must equal the number of assigned names."
        assert len(symbols) == num_companies, "The number of companies must equal the number of assigned symbols."
        # Empty db
        db(db.company).delete()
        db(db.stock_history).delete()
        for i in range(num_companies):
            # Add company to db
            id = db.company.insert(
                company_name=names[i],
                company_symbol=symbols[i],
                current_stock_value=initial_values[i]
            )
            # Initialize stock history
            db.stock_history.insert(
                company_id = id,
                stock_value = initial_values[i]
            )
    
    def load_companies(self):
        """
        Return a dictionary of company dictionaries. The key
        for each company dictionary is the company id.
        """
        companies = {}
        db_companies = db(db.company).select().as_list()
        for c in db_companies:
            companies[c['id']] = c
        return companies

    def generate_new_values(self, values, n):
        """
        Generate n new values and return the new values generated
        For now, just do a simple random walk based on last value
       
        Returns a list of new values.
        """
        new_vals = [0]*n
        for i in range(n):
            if i == 0:
                new_vals[i] = values[-1] + random.random()-0.5
            else:
                new_vals[i] = new_vals[i-1] + random.random()-0.5 
        return new_vals
    
    def check_for_updates(self, id=None):
        """
        Check whether the stock value for the given company
        is current. If not, get new values for the stock
        and update the db.
        """
        assert id is not None
        companies = self.load_companies()
        c = companies.get(id, None)
        if c is None:
            raise ValueError("Company with id \"{}\" does not exist.".format(id))
        current_time = datetime.datetime.utcnow()
        time_delta = (current_time-c['latest_update']).seconds
        if time_delta >= self.update_interval:
            # We need to generate at least one new value
            n = int(time_delta / self.update_interval)
            stock_hist = self.get_stock_price(id)
            new_vals = self.generate_new_values(stock_hist, n)
            self.append_stock_price(c['id'], new_vals)
            self.set_current_value(c['id'], new_vals[-1], current_time) 

    def get_stock_history(self, id=None, update=True):
        """
        Return either the stock history of a given company as a list
        or a dictionary of stock history lists of each company
        If update is True, make sure stock values are up to date
        Otherwise, return history AS IS.

        Returns either a list of stock prices for the given company
        or a dictionary of lists where the keys are company ids.
        """
        companies = self.load_companies()
        if id is None:
            # Get history for every company
            stock_prices = {}
            for k in companies.keys():
                if update:
                    self.check_for_updates(k)
                sp = self.get_stock_price(k)
                stock_prices[k] = sp
            return stock_prices
        #else we have a specific company
        c = companies.get(id, None)
        if c is None:
            raise ValueError("Company with id \"{}\" does not exist.".format(id))
        if update:
            self.check_for_updates(id)
        hist = self.get_stock_price(id)
        return hist
    
    def get_current_value(self, id=None, update=True):
        """
        Return either the current stock value of the given company or
        the current values of every company.
        If update is True, make sure stock value is up to date.
        Otherwise, return current value(s) AS IS.
        """
        companies = self.load_companies()
        companies_to_query = []
        if id is None:
            companies_to_query = [s for s in companies.keys()]
        else:
            companies_to_query = [id]
        # For each company, make sure they have the latest value
        if update:
            for c_id in companies_to_query:
                self.check_for_updates(c_id)
        if len(companies_to_query) == 1:
            current_value = db(db.company.id == id).select().first().current_stock_value
            return current_value
        # else
        value_dict = {}
        for k in companies_to_query:
            current_value = db(db.company.id == k).select().first().current_stock_value
            value_dict[k] = current_value
        return value_dict