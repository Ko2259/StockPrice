"""
This is the code for evaluation part, we use invest profit to evaluate our model.
"""
import datetime as dt
import pandas as pd
from pandas_datareader.data import DataReader
import requests_cache
from pandas_datareader.yahoo.headers import DEFAULT_HEADERS

from StockPrice import StockData

class StockEvaluation:
    """
    Class for evaluation

    parameters:
        model (StockPrediction): built prediction model.
        asset (float): current asset, default initial is 100.
        date (timestamp): date already invested.
        stocks (list of str): list of stocks in the prediction model.
    """
    def __init__(self, model, asset = 100):
        """
        Initialize the class.

        parameters:
            model (StockPrediction): prediction model
            asset (float): initial asset, default would be 100.
        """
        self.model = model
        self.asset = asset
        self.date = model.date_train
        self.stocks = self.model.stocks

        expire_after = dt.timedelta(days=3)
        session = requests_cache.CachedSession(cache_name='cache', expire_after=expire_after)
        session.headers = DEFAULT_HEADERS

    def invest(self, date):
        """
        Invest on the given date. The strategy is that we buy the stock with highest
        predicted profit.

        parameter:
            date (timestamp): date for investment.
        """
        if isinstance(date, str):
            date = pd.Timestamp(date)

        ### check last open day is model.date_train
        last_open = StockData.last_open_day(date - pd.Timedelta(days = 1))
        if last_open != self.model.date_train:
            raise ValueError("The last day of the train set:" +
                            self.model.date_train.strftime('%Y-%m-%d')
                             +"shoud be the last market open day before the given date: "
                             + date.strftime('%Y-%m-%d'))

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
            print(f"On {date.strftime('%Y-%m-%d')}, we invest the stock {stock_best}, "
                    f"and now the asset becomes {round(new, 5)}")
            self.asset = new
        else:
            print(f"On {date.strftime('%Y-%m-%d')}, we should not invest, asset keeps {self.asset}")

        self.date = date

    def get_return(self, date, stock):
        """
        Get the return if we buy 1 dollar stock at given date.

        parameters:
            date (timestamp): the day we buy the stock.
            stock (str): the stock symbol we want to buy.

        return:
            : (float) return if we buy 1 dollar.
        """
        data = DataReader(stock, 'yahoo', date, date)
        val_open, val_close = data.iloc[0]["Open"], data.iloc[0]["Close"]

        return val_close / val_open

    def get_open(self, date, stock):
        """
        Get the open value for the stock on given date.

        parameter:
            date (timestamp): the date
            stock (str): stock symbol
        """
        val = DataReader(stock, "yahoo", date, date).iloc[0]["Open"]

        return val

    def update(self, date):
        """
        update the predict model.
        """
        self.model.update(date, message = False)

    def evaluate(self, days = 10):
        """
        keep invest for several days.

        parameter:
            days (int): number of days we would like to invest.
        """
        date = self.date
        for _ in range(days):
            date += pd.Timedelta(days = 1)
            self.invest(date)
            self.update(date)
