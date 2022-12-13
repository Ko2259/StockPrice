"""
This is the code for ML part, we used the TBATS model
"""
import datetime as dt
import pandas as pd
from pandas_datareader.data import DataReader
import pandas_market_calendars as mcal
import requests_cache
from pandas_datareader.yahoo.headers import DEFAULT_HEADERS
from sktime.forecasting.tbats import TBATS

from stocktool import StockData

class StockPrediction:
    """
    Class for the prediction and update

    parameters:
        data (StockData): build a StockData class variable based on users request.
        train (dict): Use the stock symbol as the keys. Value is the train data
                       for the current model, has two columns: Data and price.
        y (dict): Use the srock symbol. Stores the train data. Difference from train is that
                   in y we do not store Data. We will fit model based on y.
        pred (dict): Use the stock symbol as the keys. Value stores the predicted values.
        val (str): the value we will use for prediction. Can be "Open" or "Close".
        date_pred, date_train (Timestamp): last date predicted and in train set.

    """

    def __init__(self, data = None, val = "Close", method = "TBATS",
                    stocks = ["^DJI"], start = "", end = "", period = None):
        """
        Initialize the class.

        parameters:
        data (StockData): the stock data that we will build our model.
        val: (str): The value we will use for the prediction. Default is "Close".
        method (str): ML model we will use. Default is TBATS.
        stocks, start, end, period : If data is not given, we will use these to build a
                                     a StockData class
        """
        expire_after = dt.timedelta(days=3)
        session = requests_cache.CachedSession(cache_name='cache', expire_after=expire_after)
        session.headers = DEFAULT_HEADERS

        if not data:
            self.data = StockData(stocks, start, end, period)
        else:
            self.data = data

        self.stocks = self.data.stocks
        self.train, self.y = {}, {}
        self.model = {}
        self.pred = {}
        self.val = val

        for stock in self.stocks:
            self.train[stock], self.y[stock] = self.get_train_y(self.data.df[stock])
            self.model[stock] = self.build_model(method)
            self.model[stock].fit(self.y[stock])
            self.pred[stock] = pd.DataFrame()
            self.date_pred = self.train[stock]["Date"].iloc[-1]
            self.date_train = self.date_pred
        self.burn_in = len(self.train[self.stocks[0]])

    def check_day_open(self, date):
        """
        check whether the stock market is open on the given date.

        parameter:
            date (pd.Timestamp): the given date

        return:
            : (bool) True means the stock market is open on the given date. And False otherwise.
        """
        nyse = mcal.get_calendar("NYSE")
        start, end = date - pd.Timedelta(days = 5), date + pd.Timedelta(days = 5)
        market_days = nyse.valid_days(start, end)

        return date.tz_localize("UTC") in market_days

    def get_train_y(self, df):
        """
        Helper function for building train and y variable.

        parameter:
            df (DataFrame): get from data.df[stock]
        """
        train = df.reset_index()[["Date", self.val]]
        y = train[self.val]
        return train, y

    def build_model(self, method):
        """
        build the ml model
        """
        if method == "TBATS":
            forecaster = TBATS(use_box_cox=True, use_trend=True, use_arma_errors=True, sp = 5)
        return forecaster

    def predict(self, days = 1, level = 0.95):
        """
        return the predicted values for each stock, and store the value to self.pred.

        parameters:
            days (int): number of days we want to predict. Default value is 1.
            level (float): confidence level for the prediction interval

        """
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

            ## Since this method might be called multiple times, we will only store values
            ## to self.pred if it haven't been stored.
            if index[0] > self.date_pred:
                #update
                pred_tomorrow = pd.DataFrame({stock : pred_val[:1], stock + "-low" : low[:1],
                                        stock + "-high": high[:1]}, index = index[:1])
                self.pred[stock] = pd.concat([self.pred[stock], pred_tomorrow])

        self.date_pred = index[0]
        return pred

    def update(self, date = None, message = True):
        """
        update the train set until the given date.

        parameters:
            date (str): will update the train set until the given date.
            message (bool): whether we will need to print the message. When update inside of
                            of other functions, message = False.
        """
        if not date:
            date = pd.Timestamp(pd.Timestamp.now().date()) ## take to be today
        else:
            date = pd.Timestamp(date)

        if date > pd.Timestamp.now():
            raise ValueError("Given date is after today.")

        if not self.check_day_open(date):
            if message:
                print(f"The Stock Market if not open on {date.strftime('%Y-%m-%d')}"
                    +", update until the last open date.")
            date = StockData.last_open_day(date)

        if self.date_train >= date:
            if message:
                print(f"The day {date.strftime('%Y-%m-%d')} is already contained in the model, "
                    +"no update needed")
            return

        ### update model, train, y
        for stock in self.stocks:
            data = DataReader(stock, 'yahoo', self.date_train+pd.Timedelta(days = 1), date)
            train, y = self.get_train_y(data)
            self.train[stock] = pd.concat([self.train[stock], train]).reset_index(drop = True)
            self.y[stock] = pd.concat([self.y[stock], y]).reset_index(drop = True)
            self.model[stock].update(y = self.y[stock][-len(data):])
        self.date_train = date

        return
