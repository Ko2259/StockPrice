import numpy as np
import unittest
import pandas as pd
from pandas_datareader import data as web
from datetime import datetime
from pandas_datareader._testing import skip_on_exception
from pandas_datareader._utils import RemoteDataError

from Visualization import StockData

class TestVisual(unittest.TestCase):

	'''
	Smoke test, see whether the class works
	'''
	
	def test_smoke(self):
		start_time = "2022-01-05"
		end_time = "2022-10-10"
		data = StockData(["Meta"], start_time, end_time)
		return

	'''
	test for start, end, period does not match
	'''
	def test_three_parameter(self):
		start_time = "2022-01-05"
		end_time = "2022-01-10"
		period = 6
		with self.assertRaises(ValueError):
			data = StockData(["Meta"], start_time, end_time, period)

	'''
	test for the count of open days
	'''

	def test_count_open_days(self):
		start_time = "2022-01-03"
		end_time = "2022-01-24"
		data = StockData(["Meta"], start_time, end_time)
		self.assertEqual(data.open_days, 15)
		return

	def test_count_open_days2(self):
		"""
		test for the count of open days
		"""
		start_time = "2022-01-03"
		end_time = "2022-01-22"
		data = StockData(["Meta"], start_time, end_time)
		self.assertEqual(data.open_days, 15)
		return
	

	'''
	Test whether the start date will be shifted to the last open date
	'''
	
	def test_start_not_open(self):
		start_time = "2022-01-01"
		end_time = "2022-10-10"
		data = StockData(start = start_time, end = end_time)
		self.assertEqual(data.start_ts, pd.Timestamp("2021-12-31"))
		return

	'''
	Test whether the end date witl be shifted to the last open date
	'''
	def test_end_not_open(self):
		start_time = "2022-01-03"
		end_time = "2022-01-01"
		data = StockData(start = start_time, end = end_time)
		self.assertEqual(data.end_ts, pd.Timestamp("2022-01-03"))
		return

	'''
	Test when end time is in the future
	'''
	def test_end_in_future(self):
		start_time = "2022-01-01"
		end_time = "2023-10-10"
		with self.assertRaises(ValueError):
			data = StockData(start = start_time, end = end_time)

		return

	'''
	Test when start time is after than the end time
	'''


	def test_start_after_end(self):
		start_time = "2022-01-03"
		end_time = "2021-10-3"
		with self.assertRaises(ValueError):
			data = StockData(start = start_time, end = end_time)

		return

	'''
	invalid stock name
	'''
	def test_invalid_stock(self):
		start_time = "2022-01-01"
		end_time = "2022-10-10"
		with self.assertRaises(ValueError):
			data = StockData(["Metee"], start_time, end_time)
		return

	'''
	Stock is invalid in the given date range
	'''
	def test_stock_invalid_in_time_range(self):
		with self.assertRaises(ValueError):
			data = StockData(["Meta"], "1990-01-01", "2000-01-01")
		return

if __name__ == "__main__":
	unittest.main()
	

