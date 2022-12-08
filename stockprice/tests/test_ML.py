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
		start_time = "2022-01-05"
		end_time = "2022-10-10"
		data = StockData(["Meta"], start_time, end_time)
		#model = StockPrediction(data)
		return

if __name__ == "__main__":
	unittest.main()
	

