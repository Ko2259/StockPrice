'''
from src.StockPrice_visualize import StockData
from src.StockPrice_ML import StockPrediction
data = StockData(["Meta"], "2021-01-01", "2022-10-30")

model = StockPrediction(data = data)


pred, interval = model.predict(days = 5)
print(pred.index)
'''
print(5*1000*1000*1000/(1024**3))
