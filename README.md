[![Python Package using 
Conda](https://github.com/Ko2259/StockPrice/actions/workflows/python-package-conda.yml/badge.svg)](https://github.com/Ko2259/StockPrice/actions/workflows/python-package-conda.yml)
# StockTool
A Tool for visualizing, analyzing, forecasting, and evaluating the stock price, and give user investment strategy suggestions.

## Overview

One investor might want to predict the trend for a specific stock, and to know which stock is better to invest in based on the past stock price. As stock market changing so rapidly, it might be hard to make the right investment strategy by analyzing the data manually. Thus, we built a tool for users to visualize, analyze, forecast and evaluate stocks.

## Requirements

StockTool requires a Python environment higher than Python 3.6.

## Installation

- Method 1: Install from the Pipit

	`pip install stocktool`

	If this does not work, run this command first:

	`pip install datetime pandas_datareader plotly sktime tbats requests_cache pandas_market_calendars`

- Method 2: Install from the GitHub repo

	`pip install git+https://github.com/Ko2259/StockTool.git`

- Method 3: Clone this repository and set up a virtual environment(suggested method due to the dependencies)

	1. Open the terminal
	2. Clone the repository using `git clone git@github.com:Ko2259/StockTool.git`
	3. Change the directory to StockPrice using `cd StockTool`
	4. Set up a new virtual environment using `conda env create -f environment.yml`
	5. Activate the virtual environment using `conda activate stocktool`
	6. After finish analyzing, deactivate the virtual environment using `conda deactivate`


## Usage

### Repository Structure

```bash
.
├── LICENSE
├── README.md
├── docs
│   ├── Functional_Specification.md
│   ├── milestone.md
├── environment.yml
├── example
│   ├── evaluation.ipynb
│   ├── model.ipynb
│   └── visualization.ipynb
└── stocktool
    ├── evaluation
    ├── model
    ├── tests
    └── visualization
```

The `stocktool` directory includes `visualization` module for visualize stocks, `model` module for analyze and forecast future stock price, `evaluation` module for evaluate invest profit, and unit tests in `tests` module. The `example` directory provides examples which help new users learn how to use this tool.

### Data access

- After you installing this tool on your local machine or on a virtual environment, and importing this tool using `import stocktool`, you can access stock data with built-in function below, where we read stock data through Yahoo Finance API.

	> `data = stocktool.StockData(stocks, start, end, period)`

- In the function `StockData`:

	1. you can specify one stock, or many stocks with their Dow Jones Index;
	2.  you can specify the start date and the end date, or you can only specify the start date along with a specified period.

- Then you'll get a data structure containing the pandas dataframes, start date, end date and open days.
	1. `data.df`: a dictionary contains pandas dataframe for each stock
	2. `data.start`: adjust input start date to a stock market open day
	3. `data.end`: adjust input end date to a stock market open day
	4. `data.open_days`: stock market open days

Example please refer to `StockTool/examples/visualization.ipynb`.

### Visualization

- After you accessing the `data`, you can visualize it with our built-in functions, or you can make some other plots on your own.

- Below are the visualization functions in our tool:

	1. `data.box_plot()`: to see the fluctuation for each stock during this period
	2. `data.price_plot()`: to see the stock price for each stock on every market open day
	3. `data.candle_plot()`: to see the candlestick chart for each stock on every market open day

Example please refer to `StockTool/examples/visualization.ipynb`.

### Forecasting

- After you accessing the `data`, you can train the `data` as below:

	> `model = stocktool.StockPrediction(data, val)`, where `val="Close"` or `val="Open"`

	Or you can construct the `model` without accessing the data first:

	> `model = stocktool.StockPrediction(val, stocks, start, end, period)`

- After you training the `model`, you can forecast the stock price in next few days.
	> `model.predict(days, level)`: a dictionary contains the prediction for each stock, along with the confidence interval

- You may also want to update the model with new data points, so you can update it with stock data till a new end date.
	1. first update model: `model.update(date)`
	2. then forecast using updated model: `model.predict()`

Example please refer to `StockTool/examples/model.ipynb`.

### Evaluation

- After training data in `model`, we build a method to evaluate our two investment strategies.

	1. With specified asset, the first strategy is to invest in the stock with highest predicted profit every day.
	2. The second strategy is to split asset to invest in all stocks with positive predicted profit every day.

- Here, we evaluate as below:

	1. first get the evaluation structure: `eva = stocktoll.StockEvaluation(model, asset)`
	2. after getting the evaluation structure, evaluate the strategy: `eva.evaluate(days, weighted, graph)`
	3. after evaluation, draw the graph of real stock price and predicted price: `eva.graph(stocks, days)`

Example please refer to `StockTool/examples/evaluation.ipynb`.

## But Report

If you have any issue or bug when running this tool, please submit a `New issue` in `Issues`.


## Acknowledgements

Thanks Prof. David Beck and Erin Wilson from University of Washington for their support, help and feedback in developing this tool.
