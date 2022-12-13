"""
Test for the evaluation submodule
"""
import unittest

import sys
sys.path.append("../")

from visualization import StockData
from model import StockPrediction
from evaluation import StockEvaluation


class TestVisual(unittest.TestCase):
    """
    class for tests
    """
    def test_smoke(self):
        """
        smoke test
        """
        start_time = "2022-09-01"
        end_time = "2022-10-10"
        data = StockData(["Meta"], start_time, end_time)
        model = StockPrediction(data)
        evaluation = StockEvaluation(model)
        evaluation.evaluate(days = 3)

if __name__ == "__main__":
    unittest.main()
