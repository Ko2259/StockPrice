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

class StockData:
    '''
    import the data for given stocks
    '''
    def __init__(self, stocks = ["^DJI"], start = "", end = "", period = None):
        self.df = dict()
        if (start) and (end) and period:
            if period != (pd.Timestamp(end)-pd.Timestamp(start)).days:
                raise ValueError("Does not meet the condition that end - start = period")
        if not start:
            start = pd.Timestamp(end)-pd.Timedelta(days = period)
        else:
            start = pd.Timestamp(start)

        if not end:
            end = pd.Timestamp(start)+pd.Timedelta(days = period)
        else:
            end = pd.Timestamp(end)

        self.open_days = StockData.count_open_day(start, end, period)


        self.start_ts = StockData.last_open_day(start)
        self.end_ts = StockData.next_open_day(end)

        expire_after = dt.timedelta(days=3)
        session = requests_cache.CachedSession(cache_name='cache', expire_after=expire_after)
        session.headers = DEFAULT_HEADERS


        
        ### check end time is not after today
        if end > pd.Timestamp.now():
            raise ValueError("The end time is after today")

        ### check start is before end
        if self.start_ts > self.end_ts:
            raise ValueError("The start date is after the end date")
        
        ### add message when start, end are not market open date
        if self.start_ts != start:
            print("The market is not open on the start date, automatically shifted to the last open date which is %s" 
                            %(self.start_ts.strftime("%Y-%m-%d")))
        if self.end_ts != end:
            print("The market is not open on the end date, automatically shifted to the next open date which is %s" 
                            %(self.end_ts.strftime("%Y-%m-%d")))
        
        for name in stocks:
            ### check name is a valid stock name
            try:
                self.df[name] = data.DataReader(name, 'yahoo', self.start_ts, self.end_ts, session = session)
            except:
                raise ValueError("%s is not a valid stock code in the time range (%s, %s)" 
                                 %(name, self.start_ts.strftime("%Y-%m-%d"), self.end_ts.strftime("%Y-%m-%d")))
            self.df[name]["close-open"] = [StockData.diff(x,y)[0] for x,y in zip(self.df[name]["Open"], self.df[name]["Close"])]
            self.df[name]["high-low"] = [abs(StockData.diff(x,y)[0]) for x,y in zip(self.df[name]["High"], self.df[name]["Low"])]
        return
    
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
        start_ts = start if start else end - dt.timedelta(days = period-1)
        end_ts = end if end else start + dt.timedelta(days = period-1)
        
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
    def total_inflation(self, stock = [], start = "", end = "", method = "close-open"):
        if not stock:
            stock = list(self.df.keys())
        
        start_ts = StockData.last_open_day(start) if start else self.start_ts
        end_ts = StockData.last_open_day(end) if end else self.end_ts
        
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
    def inflation(self, stock = [], start = "", end = "", method = "close-open", in_function = False):
        if not stock:
            stock = list(self.df.keys())
        
        start_ts = StockData.last_open_day(start) if start else self.start_ts
        end_ts = StockData.last_open_day(end) if end else self.end_ts
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
    def inflation_plot(self, stock = [], start = "", end = "", method = "close-open"):
        df_inflation = self.inflation(stock, start, end, method, in_function = True)
        sns.set()
        plt.figure(figsize = (10, 8))
        
        plt.subplot(1,2,1)
        df_inflation.plot.box()
        plt.title("Box Plot for Inflation")
        
        plt.subplot(1,2,2)
        df_inflation.plot()
        plt.legend()
        plt.title("Plot for the Inflation")
        plt.show()
        
         

    '''
    plot the daily price data
    '''
    def price_plot(self, stock = [], start = "", end = "", method = ["Open", "Close", "High", "Low"]):
        if not stock:
            stock = list(self.df.keys())
        
        ### add message when stock is more than 10
        
        start_ts = StockData.last_open_day(start) if start else self.start_ts
        end_ts = StockData.last_open_day(end) if end else self.end_ts
        
        date_range = pd.date_range(start = start_ts, end = end_ts)
        
        sns.set()
        plt.figure(figsize = (15, 45))
        
        for idx, name in enumerate(stock):
            plt.subplot(5, 1, idx+1)
            df_temp = self.df[name].loc[self.df[name].index.isin(date_range), :]
            for col in method:
                df_temp[col].plot()
            plt.legend()
            plt.title(name)
        plt.show()


