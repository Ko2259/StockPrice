import sys
sys.path.append('../')

import numpy as np
import unittest
import pandas as pd
from pandas_datareader import data as web
from datetime import datetime
from pandas_datareader._testing import skip_on_exception
from pandas_datareader._utils import RemoteDataError

from visualization import StockData
from ml import StockPrediction

class TestVisual(unittest.TestCase):

	def test_smoke(self):
		'''
		Smoke test, see whether the class works
		'''
		start_time = "2022-09-01"
		end_time = "2022-10-10"
		data = StockData(["Meta"], start_time, end_time)
		model = StockPrediction(data)

	def test_date_train(self):
		"""
		test whether the date_train is the same as end time
		"""
		start_time = "2022-09-01"
		end_time = "2022-10-10"
		data = StockData(["Meta"], start_time, end_time)
		model = StockPrediction(data)
		self.assertEqual(model.date_train, data.end_ts)

	def test_train_length(self):
		"""
		test whether train has the same length as open days
		from start to end
		"""
		start_time = "2022-09-01"
		end_time = "2022-10-10"
		data = StockData(["Meta"], start_time, end_time)
		model = StockPrediction(data)
		self.assertEqual(len(model.train["Meta"]), data.open_days)

	def test_train_y_length(self):
		"""
		test whether train, and y has the same length
		"""
		start_time = "2022-09-01"
		end_time = "2022-10-10"
		data = StockData(["Meta"], start_time, end_time)
		model = StockPrediction(data)
		self.assertEqual(len(model.train["Meta"]), len(model.y["Meta"]))

	def test_after_pred_date_change(self):
		"""
		test after prdiction, date_pred will move one day forward
		"""
		start_time = "2022-09-01"
		end_time = "2022-10-10"
		data = StockData(["Meta"], start_time, end_time)
		model = StockPrediction(data)
		pred = model.predict()
		self.assertEqual(model.date_pred, pd.Timestamp("2022-10-11"))

	def test_multiple_prediction(self):
		"""
		precit multiple times, data_pred should not change
		"""
		start_time = "2022-09-01"
		end_time = "2022-10-10"
		data = StockData(["Meta"], start_time, end_time)
		model = StockPrediction(data)
		for _ in range(5):
			pred = model.predict()
		self.assertEqual(model.date_pred, pd.Timestamp("2022-10-11"))

	def test_update(self):
		"""
		after update, date_train move forward
		"""
		start_time = "2022-09-01"
		end_time = "2022-10-10"
		data = StockData(["Meta"], start_time, end_time)
		model = StockPrediction(data)
		model.update("2022-10-13")
		self.assertEqual(model.date_train, pd.Timestamp("2022-10-13"))

	def test_update2(self):
		"""
		update to a stock not open date
		date_pred stopped at the last open daye
		"""
		start_time = "2022-09-01"
		end_time = "2022-10-10"
		data = StockData(["Meta"], start_time, end_time)
		model = StockPrediction(data)
		model.update("2022-10-15")
		self.assertEqual(model.date_train, pd.Timestamp("2022-10-14"))

	def test_update_predict(self):
		"""
		predict after update, date_pred move forward
		"""
		start_time = "2022-09-01"
		end_time = "2022-10-10"
		data = StockData(["Meta"], start_time, end_time)
		model = StockPrediction(data)
		model.update("2022-10-13")
		pred = model.prdiction()
		self.assertEqual(model.date_train, pd.Timestamp("2022-10-14"))









if __name__ == "__main__":
	unittest.main()
	

