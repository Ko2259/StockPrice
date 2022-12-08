import pandas as pd

from StockPrice.stock_price_visualize import StockData
from StockPrice.stock_price_ml import StockPrediction
data = StockData(["Meta", "AMZN"], "2022-10-20", "2022-11-28")
model = StockPrediction(data)

model.update("2022-12-02")
print(model.date_pred, model.date_train)
print(model.train["Meta"], model.train["AMZN"])
print(model.predict()["Meta"])
print(model.date_pred, model.date_train)