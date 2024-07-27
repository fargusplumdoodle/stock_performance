# Stock Performance Analyzer

## Overview

This Python script generates price and volume graphs for a given stock ticker. It uses historical stock data to create visual representations of stock performance over time.

## Features

- Generates price-volume plots
- Creates estimated buy-sell volume plots
- Supports multiple time periods and intervals
- Provides inception date information for stocks

## Data Source

The script uses the `yfinance` library to fetch stock data from Yahoo Finance.

## Requirements

- Python 3.x
- Required libraries: yfinance, matplotlib, numpy, pandas

You can install the required libraries using pip:

```
pip install yfinance matplotlib numpy pandas
```

## Usage

Run the script from the command line with the following syntax:

```
python stock_performance.py <ticker> [options]
```

### Arguments

- `ticker`: Stock ticker symbol (e.g., AAPL for Apple Inc.)

### Options

- `--output`: Output directory for graphs (default: ./output)
- `--no-output-dir`: Output graphs to the current directory instead of ./output
- `--periods`: List of time periods to analyze (default: 1y 3y 5y)
- `--interval`: Interval for data points (e.g., 1d, 1wk, 1mo) (default: 1d)

### Examples

1. Generate graphs for Apple Inc. with default settings:
   ```
   python stock_performance.py AAPL
   ```

2. Generate graphs for Microsoft with custom periods and interval:
   ```
   python stock_performance.py MSFT --periods 6mo 1y 2y --interval 1wk
   ```

3. Save graphs to a specific directory:
   ```
   python stock_performance.py GOOGL --output ./google_graphs
   ```

## Output

The script generates two types of graphs for each specified period:

1. Price and Volume Over Time
2. Estimated Buy/Sell Volume Over Time

Graphs are saved as PNG files in the specified output directory or the current directory if `--no-output-dir` is used.

## Note

This script is for informational purposes only and should not be considered financial advice. Always do your own research before making investment decisions.
