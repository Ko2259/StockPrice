"""
This is the code for evaluation part, we use invest profit to evaluate our model.
"""
import numpy as np
import pandas as pd
from pandas_datareader.data import DataReader
import datetime as dt
import pandas_market_calendars as mcal
from sktime.datasets import load_airline
from sktime.forecasting.tbats import TBATS
import requests_cache
from pandas_datareader.yahoo.headers import DEFAULT_HEADERS

from StockPrice import StockData, StockPrediction

class StockEvaluation:
    """
    Class for evaluation
    """
    def __init__(self, model, asset = 100):
        self.model = model
        self.asset = asset
        self.date = model.date_train
        self.stocks = self.model.stocks
        
        expire_after = dt.timedelta(days=3)
        session = requests_cache.CachedSession(cache_name='cache', expire_after=expire_after)
        session.headers = DEFAULT_HEADERS
    
    def invest(self, date):
        if isinstance(date, str):
            date = pd.Timestamp(date)
        
        ### check last open day is model.date_train
        last_open = StockData.last_open_day(date - pd.Timedelta(days = 1))
        if last_open != self.model.date_train:
            raise ValueError(f"The last day of the train set: {self.model.date_train.strftime('%Y-%m-%d')} "
                             +f"shoud be the last market open day before the given date: {date.strftime('%Y-%m-%d')}")
        
        ### check market open
        if not self.model.check_day_open(date):
            print(f"On {date.strftime('%Y-%m-%d')}, the market is not open.")
            return
        
        ### check whether date already invested
        if self.date >= date:
            print(f"Already invested on the date {date.strftime('%Y-%m-%d')}")
            return
            
        profit_max, stock_best = 0, ""
        self.model.predict()
        for stock in self.stocks:
            open_val = self.get_open(date, stock)
            close_pred = self.model.pred[stock].iloc[-1][stock]
            profit = (close_pred - open_val) / open_val
            
            if profit > profit_max:
                profit_max, stock_best = profit, stock
        
        if profit_max >0:
            new = self.get_return(date, stock_best) * self.asset
            print(f"On {date.strftime('%Y-%m-%d')}, we invest the stock {stock_best}, and now the asset becomes {round(new, 5)}")
            self.asset = new
        else:
            print(f"On {date.strftime('%Y-%m-%d')}, we should not invest, asset keeps {self.asset}")
        
        self.date = date
    
    def get_return(self, date, stock):
        data = DataReader(stock, 'yahoo', date, date)
        val_open, val_close = data.iloc[0]["Open"], data.iloc[0]["Close"]
        
        return val_close / val_open
            
    def get_open(self, date, stock):
        val = DataReader(stock, "yahoo", date, date).iloc[0]["Open"]
        
        return val
    
    def update(self, date):
        self.model.update(date, message = False)
    
    def evaluate(self, days = 10):
        date = self.date
        for _ in range(days):
            date += pd.Timedelta(days = 1)
            self.invest(date)
            self.update(date)
