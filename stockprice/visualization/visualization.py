"""
This is the code for visulization part
"""
import datetime as dt
import numpy as np
import pandas as pd
from pandas_datareader.data import DataReader
from pandas_datareader.yahoo.headers import DEFAULT_HEADERS
import pandas_market_calendars as mcal
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests_cache

class StockData:
    """
    Class for visulization and analysis

    parameters:
        df (dict): uses stock symbol as key and values are pd.DataFrame that stores
                   the stock price data
        start, end (str): the start and end date for the data
        open_days (int): number of market open days between start and end date
    """
    def __init__(self, stocks = ["^DJI"], start = "", end = "", period = None):
        """
        Initialize the class.

            Parameters:
                stocks (list of string): list of stock symbols, default case is
                                         Dow Jones index
                start, end (string): the start and end time for stock price data
                period (int): The number of days between start and end. At least
                              two of start, end, period should be given.
        """
        self.df = {}
        self.stocks = stocks
        count = 0
        if start:
            count += 1
        if end:
            count += 1
        if period:
            count += 1
        if count < 2:
            raise ValueError("At least two of start, end, period should be given")
        start, end = self.check_period(start, end, period)

        self.start_ts, self.end_ts = StockData.check_open(start, end)
        self.open_days = self.count_open_days(self.start_ts, self.end_ts)
        self.start = self.start_ts.strftime("%Y-%m-%d")
        self.end = self.end_ts.strftime("%Y-%m-%d")
        expire_after = dt.timedelta(days=3)
        session = requests_cache.CachedSession(cache_name='cache', expire_after=expire_after)
        session.headers = DEFAULT_HEADERS
        ### check end time is not after today
        if end > pd.Timestamp.now():
            raise ValueError("The end time is after today")

        ### check start is before end
        if self.start_ts > self.end_ts:
            raise ValueError("The start date is after the end date")

        for name in stocks:
            ### check name is a valid stock symbol
            try:
                self.df[name] = DataReader(name, 'yahoo', self.start_ts, self.end_ts,
                                            session = session)
            except:
                raise ValueError(f"{name} is not a valid stock code in the time range "
                    +f"({self.start_ts.strftime('%Y-%m-%d')},{self.end_ts.strftime('%Y-%m-%d')})")

            self.df[name]["close-open"] = [StockData.diff(x,y)[0] for x,y in
                                            zip(self.df[name]["Open"], self.df[name]["Close"])]
            self.df[name]["high-low"] = [abs(StockData.diff(x,y)[0]) for x,y in
                                            zip(self.df[name]["High"], self.df[name]["Low"])]

    def check_stocks(self, stocks):
        """
        Check that stocks is non-empty and every stock is in the model.
        """
        if not stocks:
            raise ValueError("list of stocks should not be empty.")

        for name in stocks:
            if not name in self.stocks:
                raise ValueError(f"{name} is not in the model.")

    def check_period(self, start, end, period):
        """
        check whether (start, end, period) is valid and return correct start, end.
        If only one or none of the parameters are given, will return the start and
        end date for the class.

        parameters:
            start, end (string): start and end time
            period (int): number of days between start and end
        return:
            start, end (pd.Timestamp): the start and time
        """
        if (start) and (end) and period:
            if period != (pd.Timestamp(end)-pd.Timestamp(start)).days:
                raise ValueError("Does not meet the condition that end - start = period")
        count = 0
        if start:
            count += 1
        if end:
            count += 1
        if period:
            count += 1

        if count == 0:
            return self.start_ts, self.end_ts
        if count == 1:
            raise ValueError("Either not give at all or give least two of start, end, period")

        if not start:
            start = pd.Timestamp(end)-pd.Timedelta(days = period-1)
        else:
            start = pd.Timestamp(start)

        if not end:
            end = pd.Timestamp(start)+pd.Timedelta(days = period-1)
        else:
            end = pd.Timestamp(end)

        return start, end

    def check_open(start, end):
        """
        Shift the start date to the latest market open day and shift the end date to
        next market open day.

        parameters:
            start, end (pd.Timestamp): the start and end date

        return:
            start_ts, end_ts (pd.Timestamp)
        """
        start_ts = StockData.last_open_day(start)
        end_ts = StockData.next_open_day(end)

        ### add message when start, end are not market open date
        if start_ts != start:
            print("The market is not open on the start date, automatically shifted to the "
                +f"last open date which is {start_ts.strftime('%Y-%m-%d')}")
        if end_ts != end:
            if end_ts >= pd.Timestamp.now():
                end_ts = StockData.last_open_day(end_ts -  pd.Timedelta(days = 1))
                print("The market is not open on the end date, and there is no next open day, "
                    +"automatically shifted to the last open date which is "
                    +f"{end_ts.strftime('%Y-%m-%d')}")
            else:
                print("The market is not open on the end date, automatically shifted to the "
                +f"next open date which is {end_ts.strftime('%Y-%m-%d')}")

        return start_ts, end_ts

    def last_open_day(date_ts):
        """
        return the last market open date before the given date

        parameter:
            date_ts (pd.Timestamp): the given date

        return:
            open_day (pd.Timestamp): the last market open date before the given date
        """
        nyse = mcal.get_calendar("NYSE")
        start =date_ts - dt.timedelta(days = 20)
        market_days = nyse.valid_days(start, date_ts)

        for i in range(20):
            open_day = date_ts - dt.timedelta(days = i)
            if open_day.tz_localize("UTC") in market_days:
                return open_day

    def next_open_day(date_ts):
        """
        return the next market open date after the given date

        parameter:
            date_ts (pd.Timestamp): the given date

        return:
            open_day (pd.Timestamp): the next market open date before the given date
        """
        nyse = mcal.get_calendar("NYSE")
        end =date_ts + dt.timedelta(days = 20)
        market_days = nyse.valid_days(date_ts, end)

        for i in range(20):
            open_day = date_ts + dt.timedelta(days = i)
            if open_day.tz_localize("UTC") in market_days:
                return open_day

    def count_open_days(self, start = "", end = "", period = None):
        """
        return the number of market open days between start and end.
        If only one or none of the parameters are given, return the
        number of open days between the start and end date of the class

        parameters:
            start, end (string): start and end date
            period (int): number of days between start and end.

        return:
            days (int): number of open days between start and end
        """
        start_ts, end_ts = self.check_period(start, end, period)
        nyse = mcal.get_calendar("NYSE")
        days = len(nyse.valid_days(start_ts, end_ts))
        return days

    def diff(a,b):
        """
        helper function, return the increment/decrement

        parameter:
            a, b (float)

        return:
            result (float): fluctuatuin from b to a
            percent (string): written result into a percentage form
        """
        result = round((b-a)/a, 4)
        percent = str(round(result*100, 2))+"%"
        return result, percent

    def total_fluctuation(self, stocks = None, start = "", end = "", period = None,
                            method = "close-open"):
        """
        return the fluctuation during the given time period

        parameters:
            stocks (list of string): a list of stock symbols, default would be all of the
                                    stocks in the class.
            start, end (string): start and end date.
            period (int): number of days between start and end.
            method (string): if method = "close-open", then the fluctuation is calculatedd
                             by the open value and close value. If method = "high-low",
                             then it is calculated by high value and low value.
        """
        if not stocks:
            stocks = self.stocks
        else:
            self.check_stocks(stocks)

        start_ts, end_ts = self.check_period(start, end, period)

        if start_ts < self.start_ts or end_ts > self.end_ts:
            raise ValueError("Time period should between in data's time range")

        start_ts, end_ts = StockData.check_open(start_ts, end_ts)

        fluctuation = {}
        if method == "close-open":
            for name in stocks:
                if start_ts < self.df[name].index[0]:
                    start_ts = self.df[name].index[0]
                fluctuation[name] = StockData.diff(self.df[name].loc[start_ts]["Close"],
                                                        self.df[name].loc[end_ts]["Open"])[1]
        else:
            for name in stocks:
                if start_ts < self.df[name].index[0]:
                    start_ts = self.df[name].index[0]
                fluctuation[name] = StockData.diff(self.df[name].loc[start_ts]["High"],
                                                        self.df[name].loc[end_ts]["Low"])[1]

        return pd.DataFrame(data = fluctuation, index = ["fluctuaion"])

    def fluctuation(self, stocks = None, start = "", end = "", period = None,
                            method = "close-open", in_function = False):
        """
        return the daily fluctuation.

        parameters:
            stocks (list of string): a list of stock symbols, default would be all of the
                                    stocks in the class.
            start, end (string): start and end date.
            period (int): number of days between start and end.
            method (string): if method = "close-open", then the fluctuation is calculatedd
                             by the open value and close value. If method = "high-low",
                             then it is calculated by high value and low value.
            in_function (bool): True means we are using this method inside some other function
                                so no message will be printed.
        """
        if not stocks:
            stocks = self.stocks
        else:
            self.check_stocks(stocks)

        start_ts, end_ts = self.check_period(start, end, period)
        start_ts, end_ts = StockData.check_open(start_ts, end_ts)

        if start_ts < self.start_ts or end_ts > self.end_ts:
            raise ValueError("Time period should between in data's time range")


        date_range = pd.date_range(start_ts, end_ts)

        result = pd.DataFrame()
        for name in stocks:
            result[name] = self.df[name].loc[self.df[name].index.isin(date_range), :][method]

        max_inc_date = result.idxmax()
        max_dec_date = result.idxmin()

        if not in_function:
            for name in stocks:
                temp = str(round(np.mean(result[name])*100, 2))+"%"
                print(f"The average for {name} is: {temp} \n")
                print(f"The max increase/min decrease of {name} occured on "
                    +f"{max_inc_date[name].strftime('%Y-%m-%d')}, which is "
                    +str(round(result[name].max()*100, 2))+"% \n")
                print(f"The max decrease/min increase of {name} occured on "
                    +f"{max_dec_date[name].strftime('%Y-%m-%d')}, which is "
                    +str(round(result[name].min()*100, 2))+"% \n")

        return result

    def get_button(self, start_ts, end_ts):
        """
        helper function for getting the button variable for plotly.
        """
        days = (end_ts - start_ts).days
        buttons = []
        if days >= 30:
            buttons.append(dict(count=1, label="1m", step="month", stepmode="backward"))
        if days >= 90:
            buttons.append(dict(count=3, label="3m", step="month", stepmode="backward"))
        if days >= 180:
            buttons.append(dict(count=6, label="6m", step="month", stepmode="backward"))
        if days >=365:
            buttons.append(dict(count=1, label="1y", step="year", stepmode="backward"))
        if days >= 365*3:
            buttons.append(dict(count=3, label="3y", step="year", stepmode="backward"))
        if days >= 365*5:
            buttons.append(dict(count=5, label="5y", step="year", stepmode="backward"))
        buttons.append(dict(step="all"))

        return buttons

    def box_plot(self, stocks = None, start = "", end = "", period = None, method = "close-open"):
        '''
        Show a box plot of fluctuation, on which you can do some customization.
        :param stocks: a sublist of self.stocks, default value is self.stocks
        :param start: a string of selected start date, should be in the range of
                      (self.start, self.end). Default value is self.start
        :param end: a string of of selected end date, should be in the range of
                    (self.start, self.end), and later than the "start" param.
                    Default value is self.end
        :param method: a string which can be "close-open" or "high-low",
                       default value is "close-open".
        '''
        df_fluctuation = self.fluctuation(stocks, start, end, period, method, in_function = True)

        if not stocks:
            stocks = self.stocks
        else:
            self.check_stocks(stocks)

        temp = ", ".join(stocks)

        fig = go.Figure()
        for s in stocks:
            fig.add_trace(go.Box(y=df_fluctuation[s],name=s))

        fig.update_layout(title = 'Box Plot for Fluctuation of ' + temp,
                          yaxis_title="Price (USD)",
                          width=900,
                          height=800)

        fig.show()

    def price_plot(self, stocks = None, start = "", end = "", period = None, method = ["Open"]):
        '''
        Show a plot of stock price, on which you can do some customization.
        :param stocks: a sublist of self.stocks, default value is self.stocks
        :param start: a string of selected start date, should be in the range
                      of (self.start, self.end). Default value is self.start
        :param end: a string of of selected end date, should be in the range
                    of (self.start, self.end), and later than the "start" param.
                    Default value is self.end.
        :param method: a sublist of ["High","Low","Open","Close"], default value is ["Open"].
        '''
        if not stocks:
            stocks = self.stocks
        else:
            self.check_stocks(stocks)

        ### add error message when input value not correct

        start_ts, end_ts = self.check_period(start, end, period)
        start_ts, end_ts = StockData.check_open(start_ts, end_ts)

        if start_ts < self.start_ts or end_ts > self.end_ts:
            raise ValueError("Time period should between in data's time range")

        date_range = pd.date_range(start_ts, end_ts)
        c = self.df[stocks[0]][method].loc[self.df[stocks[0]].index.isin(date_range)]
        c.columns = [s+"-"+stocks[0] for s in c.columns]
        for name in stocks[1:]:
            a = self.df[name][method].loc[self.df[name].index.isin(date_range)]
            a.columns = [s+"-"+name for s in a.columns]
            c = pd.concat([c,a], axis = 1)

        c_1 = c.reset_index()
        temp = ", ".join(stocks)
        fig = px.line(c_1,x="Date",y=list(c_1.columns)[1:],
                        title='Stock Price of ' + temp,render_mode='webg1')

        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons = self.get_button(start_ts, end_ts)
            )
        )

        fig.update_layout(yaxis_title="Price (USD)",
                  width=900,
                  height=600)

        fig.show()

    def candle_plot(self, stocks = None, start = "", end = "", period = None):
        '''
        Show a candlestick plot of stock price, on which you can do some customization.
        :param stocks: a sublist of self.stocks, default value is self.stocks
        :param start: a string of selected start date, should be in the range
                      of (self.start, self.end). Default value is self.start
        :param end: a string of of selected end date, should be in the range
                    of (self.start, self.end), and later than the "start" param.
                    Default value is self.end.
        '''
        if not stocks:
            stocks = self.stocks
        else:
            self.check_stocks(stocks)

        start_ts, end_ts = self.check_period(start, end, period)
        start_ts, end_ts = StockData.check_open(start_ts, end_ts)

        if start_ts < self.start_ts or end_ts > self.end_ts:
            raise ValueError("Time period should between in data's time range")


        for s in stocks:
            temp = self.df[s].loc[start_ts:][:end_ts]
            c = temp.reset_index()

            fig = go.Figure()

            # figure with secondary y-axis
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            # candlestick
            fig.add_trace(
                go.Candlestick(
                    x=c.Date,
                    open=c.Open,
                    high=c.High,
                    low=c.Low,
                    close=c.Close,
                    showlegend=False),
                row=1,
                col=1,
                secondary_y=True
            )
            fig.update_xaxes(
                rangeslider_visible = True,
                rangeselector = dict(
                    buttons = self.get_button(start_ts, end_ts)
                ))
            # volume
            fig.add_trace(
                go.Bar(x=c.Date,
                       y=c.Volume,
                       showlegend=False,
                       marker={
                           "color": "lightgrey",
                       }),
                secondary_y=False,
            )
            fig.update_layout(title="Candlestick Charts of " + s,
                              yaxis_title="Price (USD)",
                              width=900,
                              height=800)
            fig.show()
