from src.StockPrice_visualize import StockData
from src.StockPrice_ML import StockPrediction
data = StockData(["Meta"], "2017-01-01", "2022-10-30")
data.price_plot(method = ["Open", "High"])

'''
model = StockPrediction(data = data)


pred, interval = model.predict(days = 5)
print(pred.index)
'''