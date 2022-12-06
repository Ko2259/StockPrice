import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pandas_datareader import data
import datetime as dt
import pandas_market_calendars as mcal
import plotly.express as px
import requests_cache
from pandas_datareader.yahoo.headers import DEFAULT_HEADERS
from sktime.forecasting.tbats import TBATS
from collections import defaultdict

from src.stock_price_visualize import StockData

class StockPrediction:

    def __init__(self, data = None, val = "Close", method = "TBATS", stocks = ["^DJI"], start = "", end = "", period = None):
        if not data:
            self.data = StockData(stocks, start, end, period)
        else:
            self.data = data
        
        self.stocks = list(self.data.df.keys())
        self.train, self.y = {}, {}
        self.model = {}
        self.pred = {}
        self.date = {}

        for stock in self.stocks:
            self.train[stock], self.y[stock] = self.get_train_y(self.data.df[stock], val)
            self.model[stock] = self.build_model(method)
            self.model[stock].fit(self.y[stock])
            self.pred[stock] = pd.DataFrame()
            self.date[stock] = self.train[stock]["Date"].iloc[-1]


    def get_train_y(self, df, val):
        train = df.reset_index()[["Date", val]]
        y = train[val]
        return train, y

    def build_model(self, method):
        forecaster = TBATS(use_box_cox=True, use_trend=True, use_arma_errors=True)
        return forecaster

    def predict(self, days = 1, level = 0.95):
        pred = {}
        #interval = defaultdict(list)
        fh = list(range(1,days+1))
        
        start_day = self.train[self.stocks[0]]["Date"].iloc[-1]
        index = []
        for _ in range(days):
            start_day = StockData.next_open_day(start_day+pd.Timedelta(days = 1))
            index.append(start_day)

        
        for stock in self.stocks:
            pred_val = self.model[stock].predict(fh = fh).values
            temp = self.model[stock].predict_interval(fh = fh, coverage = level).values
            low = [x[0] for x in temp]
            high = [x[1] for x in temp]

            pred[stock] = pd.DataFrame({stock : pred_val, stock + "-low" : low,
                                        stock + "-high": high}, index = index)
            if index[0] > self.date[stock]:
                pass ### update the self.pred and self.date
            
        return pred

    '''
    def update(date = ""):
        ## throw value error if date is not today
        if date = 
    '''   
















