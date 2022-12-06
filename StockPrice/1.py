from src.stock_price_visualize import StockData
from src.stock_price_ml import StockPrediction
data = StockData(["Meta"], "2022-10-20", "2022-10-30")
model = StockPrediction(data)

print(model.date)
