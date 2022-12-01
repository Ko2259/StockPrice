import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pandas_datareader.data import DataReader
import datetime as dt
import pandas_market_calendars as mcal
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests_cache
from pandas_datareader.yahoo.headers import DEFAULT_HEADERS

class StockData:
    '''
    import the data for given stocks
    '''
    def __init__(self, stocks = ["^DJI"], start = "", end = "", period = None):
        self.df = dict()
        
        start, end = self.check_period(start, end, period)

        self.open_days = StockData.count_open_day(start, end, period)

        self.start_ts, self.end_ts = check_open(start, end)

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
            ### check name is a valid stock name
            try:
                self.df[name] = DataReader(name, 'yahoo', self.start_ts, self.end_ts, session = session)
            except:
                raise ValueError("%s is not a valid stock code in the time range (%s, %s)" 
                                 %(name, self.start_ts.strftime("%Y-%m-%d"), self.end_ts.strftime("%Y-%m-%d")))
            self.df[name]["close-open"] = [StockData.diff(x,y)[0] for x,y in zip(self.df[name]["Open"], self.df[name]["Close"])]
            self.df[name]["high-low"] = [abs(StockData.diff(x,y)[0]) for x,y in zip(self.df[name]["High"], self.df[name]["Low"])]
        return

    def check_period(self, start, end, period):
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

        if count < 2:
            return self.start_ts, self.end_ts

        if not start:
            start = pd.Timestamp(end)-pd.Timedelta(days = period-1)
        else:
            start = pd.Timestamp(start)

        if not end:
            end = pd.Timestamp(start)+pd.Timedelta(days = period-1)
        else:
            end = pd.Timestamp(end)

        return start, end

    def check_open(self, start, end):
        start_ts = StockData.last_open_day(start)
        end_ts = StockData.next_open_day(end)

        ### add message when start, end are not market open date
        if start_ts != start:
            print("The market is not open on the start date, automatically shifted to the last open date which is %s" 
                            %(self.start_ts.strftime("%Y-%m-%d")))
        if end_ts != end:
            print("The market is not open on the end date, automatically shifted to the next open date which is %s" 
                            %(self.end_ts.strftime("%Y-%m-%d")))

        return start_ts, end_ts
    
    '''
    return the last market open day before the give date
    '''
    def last_open_day(date_ts):
        nyse = mcal.get_calendar("NYSE")
        start =date_ts - dt.timedelta(days = 20) 
        market_days = nyse.valid_days(start, date_ts)
        
        for i in range(20):
            temp = date_ts - dt.timedelta(days = i)
            if temp.tz_localize("UTC") in market_days:
                return temp 
    '''
    return the next market open day after the given date
    '''
    def next_open_day(date_ts):
        nyse = mcal.get_calendar("NYSE")
        end =date_ts + dt.timedelta(days = 20) 
        market_days = nyse.valid_days(date_ts, end)
        
        for i in range(20):
            temp = date_ts + dt.timedelta(days = i)
            if temp.tz_localize("UTC") in market_days:
                return temp 
    
    '''
    return the count of open days in date_range
    '''
    def count_open_day(start , end , period = None):
        ### add test for three parameters, al least two should be not emply. If all parameters are given
        ### they should match
        start_ts, end_ts = self.check_period(start, end, period)
        nyse = mcal.get_calendar("NYSE")
        return len(nyse.valid_days(start_ts, end_ts))
        
        
    
    '''
    compute the inflation, return a string of percentage
    '''
    def diff(a,b):
        result = round((b-a)/a, 4)
        return result, str(round(result*100, 2))+"%"
    
    
    
    '''
    get the inflation from start to end
    '''
    def total_inflation(self, stock = [], start = "", end = "", period = None, method = "close-open"):
        if not stock:
            stock = list(self.df.keys())
        
        start_ts, end_ts = self.check_period(start, end, period)
        start_ts, end_ts = self,check_open(start_ts, end_ts)

        inflation = dict()
        if method == "close-open":
            for name in stock:
                inflation[name] = StockData.diff(self.df[name].loc[start_ts]["Close"], self.df[name].loc[end_ts]["Open"])[1]
        else:
            for name in stock:
                inflation[name] = StockData.diff(self.df[name].loc[start_ts]["High"], self.df[name].loc[end_ts]["Low"])[1]
        
        return pd.DataFrame(data = inflation, index = ["inflation"])
    
    
    
    '''
    get the inflation for every day
    '''
    def inflation(self, stock = [], start = "", end = "", period = None, method = "close-open", in_function = False):
        if not stock:
            stock = list(self.df.keys())
        
        start_ts, end_ts = self.check_period(start, end, period)
        start_ts, end_ts = self,check_open(start_ts, end_ts)

        date_range = pd.date_range(start_ts, end_ts)
        
        result = pd.DataFrame()
        for name in stock:
            result[name] = self.df[name].loc[self.df[name].index.isin(date_range), :][method]
        
        max_inc_date = result.idxmax()
        max_dec_date = result.idxmin()
        
        if not in_function:
            for name in stock:
                print("The average for %s is: %s \n" %(name, str(round(np.mean(result[name])*100, 2))+"%"))
                print("The max increase/min decrease of %s occured on %s, which is %s \n " 
                  %(name, max_inc_date[name].strftime("%Y-%m-%d"), str(round(result[name].max()*100, 2))+"%"))
                print("The max decrease/min increase of %s occured on %s, which is %s \n" 
                  %(name, max_dec_date[name].strftime("%Y-%m-%d"), str(round(result[name].min()*100, 2))+"%"))
            
        return result
    
    
    '''
    plot the daily inflation
    '''
    def inflation_plot(self, stock = [], start = "", end = "", period = None, method = "close-open"):
        df_inflation = self.inflation(stock, start, end, period, method, in_function = True)
        #sns.set()
        fig, axes = plt.subplots(nrows=1, ncols=2)
        fig.set_figheight(10)
        fig.set_figwidth(15)

        df_inflation.boxplot(ax = axes[0])
        axes[0].set_title("Box Plot for Inflation")

        df_inflation.plot(ax = axes[1])
        axes[1].set_title("Plot for the Inflation")
        
        plt.show()
        
         

    def price_plot(self, stock = [], start = "", end = "", period = None, method = ["Open"]):
        '''
        Show a plot of stock price, on which you can do some customization.
        :param stock: a sublist of self.stock, default value is self.stock
        :param start: a string of selected start date, should be in the range of (self.start, self.end).
                      Default value is self.start
        :param end: a string of of selected end date, should be in the range of (self.start, self.end), 
                    and later than the "start" param. Default value is self.end
        :param method: a sublist of ["High","Low","Open","Close"], default value is ["Open"].
        '''
        if not stock:
            stock = list(self.df.keys())
        
        ### add warning when stock is more than 10
        ### add error message when input value not correct
        
        start_ts, end_ts = self.check_period(start, end, period)
        start_ts, end_ts = self,check_open(start_ts, end_ts)

        c = self.df[stock[0]][method]
        c.columns = [s+"-"+stock[0] for s in c.columns]
        for i in range(1,len(stock)):
            a = self.df[stock[i]][method]
            a.columns = [s+"-"+stock[i] for s in a.columns]
            c = pd.concat([c,a], axis = 1)
        c.loc[start_ts:][:end_ts]
        
        c1 = c.reset_index()
        temp = ", ".join(stock)
        fig = px.line(c1,x="Date",y=list(c1.columns)[1:],title='Stock Price of ' + temp,render_mode='webg1')
        
        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ])
            )
        )
        
        fig.update_layout(yaxis_title="Price (USD)",
                  width=900,
                  height=600)
        
        fig.show()
        
        
     


    def candle_plot(self, stock = [], start = "", end = "", period = None):
        '''
        Show a candlestick plot of stock price, on which you can do some customization.
        :param stock: a sublist of self.stock, default value is self.stock
        :param start: a string of selected start date, should be in the range of (self.start, self.end).
                      Default value is self.start
        :param end: a string of of selected end date, should be in the range of (self.start, self.end), 
                    and later than the "start" param. Default value is self.end
        '''
        if not stock:
            stock = list(self.df.keys())

        start_ts, end_ts = self.check_period(start, end, period)
        start_ts, end_ts = self,check_open(start_ts, end_ts)

        
        for s in stock:
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
                rangeslider_visible=True,
                rangeselector=dict(
                    buttons=list([
                        dict(count=1, label="1m", step="month", stepmode="backward"),
                        dict(count=6, label="6m", step="month", stepmode="backward"),
                        dict(count=1, label="1y", step="year", stepmode="backward"),
                        dict(step="all")
                    ])
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


