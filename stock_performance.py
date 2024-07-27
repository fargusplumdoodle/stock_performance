import yfinance as yf
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import argparse
import os
import sys


def get_stock_data(ticker, period, interval):
    """Fetch stock data for a given ticker, period, and interval."""
    stock = yf.Ticker(ticker)
    return stock.history(period=period, interval=interval)


def calculate_buy_sell_volumes(data):
    """Calculate estimated buy and sell volumes."""
    buy_volume = data['Volume'] * (data['Close'] - data['Low']) / (data['High'] - data['Low'])
    sell_volume = data['Volume'] * (data['High'] - data['Close']) / (data['High'] - data['Low'])

    # Handle cases where High and Low are the same (prevents division by zero)
    buy_volume = buy_volume.fillna(data['Volume'] / 2)
    sell_volume = sell_volume.fillna(data['Volume'] / 2)

    return buy_volume, sell_volume


def prepare_price_volume_data(data):
    """Prepare data for price-volume plot."""
    return {
        'dates': data.index,
        'volume': data['Volume'],
        'close': data['Close']
    }


def prepare_buy_sell_volume_data(data):
    """Prepare data for buy-sell volume plot."""
    buy_volume, sell_volume = calculate_buy_sell_volumes(data)
    return {
        'dates': data.index,
        'buy_volume': buy_volume,
        'sell_volume': sell_volume
    }


def render_price_volume_plot(plot_data, ticker, period, interval):
    """Render the price-volume plot."""
    fig, ax1 = plt.subplots(figsize=(12, 6))

    # Plot volume on the first y-axis
    ax1.bar(plot_data['dates'], plot_data['volume'], width=1, alpha=0.3, color='b', label='Volume')
    ax1.set_xlabel('Date')
    ax1.set_ylabel('Volume', color='b')
    ax1.tick_params(axis='y', labelcolor='b')

    # Create a second y-axis for price
    ax2 = ax1.twinx()
    ax2.plot(plot_data['dates'], plot_data['close'], color='r', label='Closing Price')
    ax2.set_ylabel('Price', color='r')
    ax2.tick_params(axis='y', labelcolor='r')

    plt.title(f'{ticker} Price and Volume Over Time ({period}, {interval} interval)')
    fig.legend(loc='upper left', bbox_to_anchor=(0.1, 1), bbox_transform=ax1.transAxes)
    plt.xticks(rotation=45)
    plt.tight_layout()


def render_buy_sell_volume_plot(plot_data, ticker, period, interval):
    """Render the buy-sell volume plot."""
    fig, ax = plt.subplots(figsize=(12, 6))

    # Create stacked bar chart
    ax.bar(plot_data['dates'], plot_data['buy_volume'], color='green', alpha=0.6, label='Estimated Buy Volume')
    ax.bar(plot_data['dates'], plot_data['sell_volume'], bottom=plot_data['buy_volume'], color='red', alpha=0.6,
           label='Estimated Sell Volume')

    ax.set_xlabel('Date')
    ax.set_ylabel('Volume')
    ax.set_title(f'{ticker} Estimated Buy/Sell Volume Over Time ({period}, {interval} interval)')
    ax.legend()

    plt.xticks(rotation=45)
    plt.tight_layout()


def save_plot(filename, output_dir):
    """Save the current plot to a file and close it."""
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        filename = os.path.join(output_dir, filename)
    plt.savefig(filename)
    plt.close()
    print(f"Graph saved as {filename}")


def plot_price_volume(ticker, period, interval, output_dir):
    """Orchestrate the creation and saving of price and volume plots."""
    data = get_stock_data(ticker, period, interval)

    if data.empty:
        print(f"No data available for {ticker} with period {period} and interval {interval}")
        return

    # Prepare and render price-volume plot
    price_volume_data = prepare_price_volume_data(data)
    render_price_volume_plot(price_volume_data, ticker, period, interval)
    save_plot(f"{ticker}_{period}_{interval}_price_volume.png", output_dir)

    # Prepare and render buy-sell volume plot
    buy_sell_volume_data = prepare_buy_sell_volume_data(data)
    render_buy_sell_volume_plot(buy_sell_volume_data, ticker, period, interval)
    save_plot(f"{ticker}_{period}_{interval}_buy_sell_volume.png", output_dir)

    print(f"Data points for {period} with {interval} interval: {len(data)}")


def get_inception_info(ticker):
    """Get inception date and days since inception for a stock."""
    data = get_stock_data(ticker, "max", "1d")
    if data.empty:
        return None, None
    inception_date = data.index[0].date()
    days_since_inception = (datetime.now().date() - inception_date).days
    return inception_date, days_since_inception


def print_inception_info(ticker, inception_date, days_since_inception):
    """Print inception information for a stock."""
    if inception_date and days_since_inception:
        print(f"\n{ticker} inception date: {inception_date}")
        print(f"Days since inception: {days_since_inception}")
        if days_since_inception < 5 * 365:
            print(f"Note: {ticker} has been trading for less than 5 years. The 5-year graph may show incomplete data.")
    else:
        print(f"No data found for {ticker}. Please check if the ticker is correct.")


def ensure_to_suffix(ticker):
    """Ensure the ticker ends with .TO if no suffix is provided."""
    return ticker if '.' in ticker else f"{ticker}.TO"


def validate_period(period):
    """Validate the period argument."""
    valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    if period not in valid_periods:
        raise ValueError(f"Invalid period: {period}. Valid periods are: {', '.join(valid_periods)}")
    return period


def validate_interval(interval):
    """Validate the interval argument."""
    valid_intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
    if interval not in valid_intervals:
        raise ValueError(f"Invalid interval: {interval}. Valid intervals are: {', '.join(valid_intervals)}")
    return interval


def main(ticker, output_dir, periods, interval):
    ticker = ensure_to_suffix(ticker)
    for period in periods:
        plot_price_volume(ticker, period, interval, output_dir)
    inception_date, days_since_inception = get_inception_info(ticker)
    print_inception_info(ticker, inception_date, days_since_inception)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate price and volume graphs for a given stock ticker.")
    parser.add_argument("ticker", type=str, help="Stock ticker symbol (e.g., XEQT for XEQT.TO)")
    parser.add_argument("--output", type=str, default="./output",
                        help="Output directory for graphs (default: ./output)")
    parser.add_argument("--no-output-dir", action="store_true",
                        help="Output graphs to current directory instead of ./output")
    parser.add_argument("--periods", nargs='+', default=["1y", "3y", "5y"],
                        help="List of time periods to analyze (default: 1y 3y 5y)")
    parser.add_argument("--interval", type=str, default="1d",
                        help="Interval for data points (e.g., 1d, 1wk, 1mo) (default: 1d)")
    args = parser.parse_args()

    try:
        output_dir = None if args.no_output_dir else args.output
        validated_periods = [validate_period(period) for period in args.periods]
        validated_interval = validate_interval(args.interval)
        main(args.ticker, output_dir, validated_periods, validated_interval)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)