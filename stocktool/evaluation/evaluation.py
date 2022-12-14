"""
This is the code for evaluation part, we use invest profit to evaluate our model.
"""
import datetime as dt
import pandas as pd
from pandas_datareader.data import DataReader
import requests_cache
from pandas_datareader.yahoo.headers import DEFAULT_HEADERS
import plotly.express as px

from stocktool import StockData, StockPrediction

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

    def check_stocks(self, stocks):
        """
        Check that stocks is non-empty and every stock is in the model.
        """
        if not stocks:
            raise ValueError("list of stocks should not be empty.")

        for name in stocks:
            if not name in self.stocks:
                raise ValueError(f"{name} is not in the model.")

    def invest(self, date, weighted = False):
        """
        Invest on the given date. The strategy is that we buy the stock with highest
        predicted profit.

        parameter:
            date (timestamp): date for investment.
            weighted (bool): True means we will invest on all the stocks that has
                             positive predicted profit. Default is False, means we
                             will only invest the stock with the largest predicted
                             profit.
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
        profit_positive = []
        self.model.predict()
        for stock in self.stocks:
            open_val = self.get_open(date, stock)
            close_pred = self.model.pred[stock].iloc[-1][stock]
            profit = (close_pred - open_val) / open_val
            if profit > profit_max:
                profit_max, stock_best = profit, stock
            if profit > 0:
                profit_positive.append([profit, stock])

        if profit_max <= 0:
            print(f"On {date.strftime('%Y-%m-%d')}, we should not invest, "
                    + f"asset keeps {self.asset}")
        else:
            if not weighted:
                new = self.get_return(date, stock_best) * self.asset
                print(f"On {date.strftime('%Y-%m-%d')}, we invest the stock {stock_best}, "
                    f"and now the asset becomes {round(new, 5)}")
            else:
                total_profit = sum(profit for profit, stock in profit_positive)
                new = sum(self.get_return(date, stock) * self.asset * profit / total_profit
                            for profit, stock in profit_positive)
                stocks = [stock for profit, stock in profit_positive]
                print(f"On {date.strftime('%Y-%m-%d')}, we invest on {len(profit_positive)}"
                        +f" stocks, which are {','.join(stocks)},"
                        +f" and asset becomes {round(new, 5)}")
            self.asset = new

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

    def evaluate(self, days = 10, weighted = False, graph = False):
        """
        keep invest for several days.

        parameter:
            days (int): number of days we would like to invest.
            weighted (bool): whether we shold use weighted investment
                             stragy in invest method.
        """
        date = self.date
        if graph:
            index = [date]
            asset = [self.asset]
        for _ in range(days):
            date += pd.Timedelta(days = 1)
            self.invest(date, weighted)
            self.update(date)
            if graph:
                index.append(date)
                asset.append(self.asset)

        if graph:
            graph_data = pd.DataFrame(data = {"date": index, "asset": asset})

            fig = px.line(graph_data,x="date",y=list(graph_data.columns)[1:],
                        title='Asset' ,render_mode='webg1')

            fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons = self.get_button(days)
                )
            )

            fig.update_layout(yaxis_title="Price (USD)",
                  width=900,
                  height=600)

            fig.show()

    def get_button(self, days):
        """
        helper function for getting the button variable for plotly.
        """
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

    def graph(self, stocks = None, days = None):
        """
        plot the predicted value vs real value.

        parameters:
            stocks (list of str): stock symbols
            days (int): number of days we want to plot,
                         should not exceed the predicted days.
        """
        if not stocks:
            stocks = self.stocks
        else:
            self.check_stocks(stocks)

        if not days:
            days = len(self.model.pred[stocks[0]])
        else:
            if days > len(self.model.pred[stocks[0]]):
                raise ValueError(f"only {len(self.model.pred)} predicted days in the model.")

        graph_data = {}
        for name in stocks:
            graph_data[name+"-pred"] = self.model.pred[name][name][:days].values
            temp = self.model.train[name][self.model.val]
            graph_data[name] = temp[self.model.burn_in: self.model.burn_in + days].values

        pred = pd.DataFrame(data = graph_data, index = self.model.pred[stocks[0]].index[:days])
        pred.reset_index(inplace = True)

        fig = px.line(pred,x="index",y=list(pred.columns)[1:],
                        title='Predicted Stock Price' ,render_mode='webg1')

        fig.update_xaxes(
            rangeslider_visible=True,
            rangeselector=dict(
                buttons = self.get_button(days)
            )
        )

        fig.update_layout(yaxis_title="Price (USD)",
                  width=900,
                  height=600)

        fig.show()
