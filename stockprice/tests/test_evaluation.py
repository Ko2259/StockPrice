"""
Test for the evaluation submodule
"""
import unittest
import pandas as pd

import sys
sys.path.append("../")

from visualization import StockData
from ml import StockPrediction
from evaluation import StockEvaluation

class TestVisual(unittest.TestCase):
    
    def test_smoke(self):
        start_time = "2022-09-01"
        end_time = "2022-10-10"
        data = StockData(["Meta"], start_time, end_time)
        model = StockPrediction(data)
        evaluation = StockEvaluation(model)
        evaluation.evaluate(days = 3)
        #evaluation.graph(stocks = ["AMZN"])
        #self.assertRaise(ValueError)
        
if __name__ == "__main__":
    unittest.main()