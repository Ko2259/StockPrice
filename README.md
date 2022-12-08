# StockPrice
A Tool for visualize and forecast the stock price, and give user investment strategy.

## Overview

One investor might want to predict the trend for a specific stock, and to know which stock is better to invest in based on the past stock price. As stock market changed so rapidly, it might be hard to make the right investment strategy by analyzing the data manually. Thus, we built a tool for users to visualize, analyze and forecast stocks

## Requirements

StockPrice requires a Python environment higher than Python 3.0.

## Installation

- Method 1: Install StockPrice tool using command line

	`pip install git+https://github.com/Ko2259/Stock_Price.git`

- Method 2: Clone this repository and set up a virtual environment(suggested method due to the dependencies)

	1. Open the terminal
	2. Clone the repository using `git clone git@github.com:Ko2259/StockPrice.git`
	3. Change the directory to StockPrice using `cd StockPrice`
	4. Set up a new virtual environment using `condo env create -f environment.yml`
	5. Activate the virtual environment using `condo activate stockprice`
	6. After finish analyzing, deactivate the virtual environment using `condo deactivate`


## Usage

### Repository Structure

```bash
.
├── LICENSE
├── README.md
├── stockprice
│   ├── evaluation
│   ├── ml
│   ├── visualization
│   └── tests
├── docs
│   ├── Functional_Specification.md
│   ├── Technology Review.key
│   ├── milestone.mdg
└── example
```

The `stockprice` directory includes `visualization` module for visualize stocks, `ml` module for forecast future stock price, `evaluation` module for evaluate invest profit, and unit tests in `test` module. The `example` directory provides an example which help new users learn how to use this tool.

### Data access

### Visualization

### Forecasting

### Evaluation


## Contributions


## Acknowledgements
