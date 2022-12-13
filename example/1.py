
import sys
sys.path.append('../')

import pandas as pd
from sktime.forecasting.tbats import TBATS

from stockprice import StockData, StockPrediction, StockEvaluation


'''
data = StockData(["Meta", "AMZN"], "2022-10-20", "2022-11-28")
model = StockPrediction(data)
model.predict()
'''

'''
model.update("2022-12-02")
print(model.date_pred, model.date_train)
print(model.train["Meta"], model.train["AMZN"])
print(model.predict()["Meta"])
print(model.date_pred, model.date_train)
'''
'''
data = StockData(["Meta", "AMZN", "MSFT", "AAPL", "MCD", "COST", "TM"], "2022-04-01", "2022-06-01")
model = StockPrediction(data)

eva = StockEvaluation(model, asset = 100)
eva.evaluate(20, weighted = True, graph = True)
'''
