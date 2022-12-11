"""
Test for the visualization submodule
"""
import unittest
import pandas as pd

from visualization import StockData

class TestVisual(unittest.TestCase):
    """
    Test class
    """
    def test_smoke(self):
        """
        Smoke test, see whether the class works
        """
        start_time = "2022-01-05"
        end_time = "2022-10-10"
        data = StockData(["Meta"], start_time, end_time)

    def test_three_parameter(self):
        """
        test for start, end, period does not match
        """
        start_time = "2022-01-05"
        end_time = "2022-01-10"
        period = 6
        with self.assertRaises(ValueError):
            data = StockData(["Meta"], start_time, end_time, period)

    def test_count_open_days(self):
        '''
    test for the count of open days
    '''
        start_time = "2022-01-03"
        end_time = "2022-01-24"
        data = StockData(["Meta"], start_time, end_time)
        self.assertEqual(data.open_days, 15)

    def test_count_open_days2(self):
        """
        test for the count of open days
        """
        start_time = "2022-01-03"
        end_time = "2022-01-22"
        data = StockData(["Meta"], start_time, end_time)
        self.assertEqual(data.open_days, 15)

    def test_open_days3(self):
        """
        test whether open days equals length of data frame
        """
        start_time = "2022-01-03"
        end_time = "2022-05-22"
        data = StockData(["Meta"], start_time, end_time)
        self.assertEqual(data.open_days, len(data.df["Meta"]))

    def test_start_not_open(self):
        """
        Test whether the start date will be shifted to the last open date
        """
        start_time = "2022-01-01"
        end_time = "2022-10-10"
        data = StockData(start = start_time, end = end_time)
        self.assertEqual(data.start_ts, pd.Timestamp("2021-12-31"))

    def test_end_not_open(self):
        """
        Test whether the end date witl be shifted to the last open date
        """
        start_time = "2022-01-03"
        end_time = "2022-01-01"
        data = StockData(start = start_time, end = end_time)
        self.assertEqual(data.end_ts, pd.Timestamp("2022-01-03"))

    def test_end_in_future(self):
        """
        Test when end time is in the future
        """
        start_time = "2022-01-01"
        end_time = "2023-10-10"
        with self.assertRaises(ValueError):
            data = StockData(start = start_time, end = end_time)

    def test_start_after_end(self):
        """
        Test when start time is after than the end time
        """
        start_time = "2022-01-03"
        end_time = "2021-10-3"
        with self.assertRaises(ValueError):
            data = StockData(start = start_time, end = end_time)

    def test_invalid_stock(self):
        """
        invalid stock name
        """
        start_time = "2022-01-01"
        end_time = "2022-10-10"
        with self.assertRaises(ValueError):
            data = StockData(["Metee"], start_time, end_time)

    def test_only_one_period(self):
        """
        throw valuerror if only period is given
        """
        start_time = "2022-06-01"
        end_time = "2022-10-10"
        data = StockData(["Meta"], start_time, end_time)
        with self.assertRaises(ValueError):
            data.total_fluctuation(period = 10)

    def test_start_end_out_range(self):
        """
        throw value error when the date is out of range
        """
        start_time = "2022-06-01"
        end_time = "2022-10-10"
        data = StockData(["Meta"], start_time, end_time)
        with self.assertRaises(ValueError):
            data.total_fluctuation(start = "2022-05-01", end = "2022-10-01")

    def test_stock_invalid_in_time_range(self):
        """
        Stock is invalid in the given date range
        """
        with self.assertRaises(ValueError):
            data = StockData(["Meta"], "1990-01-01", "2000-01-01")

    def test_stock_not_in_model(self):
        """
        Stock is not in the model
        """
        start_time = "2022-06-01"
        end_time = "2022-10-10"
        data = StockData(["Meta"], start_time, end_time)
        with self.assertRaises(ValueError):
            data.price_plot(stocks = ["Meta", "AMZN"])

    def test_stock_empty(self):
        """
        when the input stock is empty
        """
        start_time = "2022-06-01"
        end_time = "2022-10-10"
        data = StockData(["Meta"], start_time, end_time)
        columns = data.total_fluctuation().columns
        self.assertEqual(columns, data.stocks)

if __name__ == "__main__":
    unittest.main()
