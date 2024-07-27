from fastapi import FastAPI, Query, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import yfinance as yf
from datetime import datetime

app = FastAPI()


def get_stock_data(ticker: str, period: str, interval: str):
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


def validate_period(period: str) -> str:
    """Validate the period argument."""
    valid_periods = ['1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max']
    if period not in valid_periods:
        raise ValueError(f"Invalid period: {period}. Valid periods are: {', '.join(valid_periods)}")
    return period


def validate_interval(interval: str) -> str:
    """Validate the interval argument."""
    valid_intervals = ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo']
    if interval not in valid_intervals:
        raise ValueError(f"Invalid interval: {interval}. Valid intervals are: {', '.join(valid_intervals)}")
    return interval


class StockDataMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/performance"):
            try:
                # Extract and validate query parameters
                stock = request.query_params.get("stock")
                if not stock:
                    return JSONResponse(status_code=400, content={"detail": "Stock symbol is missing"})

                periods = request.query_params.get("periods", "1y").split(",")
                interval = request.query_params.get("interval", "1d")

                validated_periods = [validate_period(period) for period in periods]
                validated_interval = validate_interval(interval)

                data = {}
                for period in validated_periods:
                    stock_data = get_stock_data(stock, period, validated_interval)
                    if stock_data.empty:
                        return JSONResponse(
                            status_code=404,
                            content={
                                "detail": f"No data available for {stock} with period {period} and interval {validated_interval}"}
                        )
                    data[period] = stock_data

                request.state.stock_data = data
                request.state.validated_periods = validated_periods
                request.state.validated_interval = validated_interval
            except ValueError as e:
                return JSONResponse(status_code=400, content={"detail": str(e)})
            except Exception as e:
                return JSONResponse(status_code=500, content={"detail": f"An error occurred: {str(e)}"})

        response = await call_next(request)
        return response


app.add_middleware(StockDataMiddleware)


@app.get("/performance/total_volume")
async def get_total_volume(request: Request):
    result = {}
    for period, data in request.state.stock_data.items():
        result[period] = {
            "dates": data.index.strftime('%Y-%m-%d').tolist(),
            "total_volume": data['Volume'].tolist()
        }
    return result


@app.get("/performance/buy_sell_volume")
async def get_buy_sell_volume(request: Request):
    result = {}
    for period, data in request.state.stock_data.items():
        buy_volume, sell_volume = calculate_buy_sell_volumes(data)
        result[period] = {
            "dates": data.index.strftime('%Y-%m-%d').tolist(),
            "buy_volume": buy_volume.tolist(),
            "sell_volume": sell_volume.tolist()
        }
    return result


@app.get("/performance/price")
async def get_price(request: Request):
    result = {}
    for period, data in request.state.stock_data.items():
        result[period] = {
            "dates": data.index.strftime('%Y-%m-%d').tolist(),
            "open": data['Open'].tolist(),
            "high": data['High'].tolist(),
            "low": data['Low'].tolist(),
            "close": data['Close'].tolist()
        }
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)