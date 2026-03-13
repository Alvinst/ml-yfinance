import time
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
import logging
import uvicorn
import yfinance as yf


# Standardized format for Fail2ban to read easily
LOG_CONFIG = {
    "version": 1,
    "formatters": {
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(client_addr)s - "%(request_line)s" %(status_code)s',
        },
    },
    "handlers": {
        "access": {
            "class": "logging.FileHandler",
            "filename": "/var/log/uvicorn/access.log",
            "formatter": "access",
        },
    },
    "loggers": {
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
}

# Initialize the FastAPI app
app = FastAPI(
    title="Stock History API",
    description="An API to fetch historical stock data using yfinance."
)

print("running v1.2...")


@app.get("/health", response_class=PlainTextResponse)
async def health_check():
    return "OK"


@app.get("/api/stock/{ticker}")
async def get_stock_history(
    ticker: str,
    period: str = Query(
        default="1mo", 
        description="Valid periods: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max"
    )
):
    """
    Fetch historical market data for a given ticker symbol.
    """
    try:
        # Initialize the Ticker object
        stock = yf.Ticker(ticker)
        
        # Fetch the historical data using the specified period
        history_df = stock.history(period=period)
        
        # Handle cases where the ticker is invalid or returns no data
        if history_df.empty:
            raise HTTPException(
                status_code=404, 
                detail=f"No historical data found for ticker '{ticker}' with period '{period}'."
            )
            
        # Convert datetime index to string for clean JSON serialization
        history_df.index = history_df.index.strftime('%Y-%m-%d')
        
        # Convert the Pandas DataFrame to a dictionary
        data_dict = history_df.to_dict(orient="index")
        
        return {
            "success": True,
            "ticker": ticker.upper(),
            "period": period,
            "rows": len(data_dict),
            "data": data_dict
        }
        
    except Exception as e:
        # Catch any unexpected errors from yfinance
        raise HTTPException(status_code=500, detail=str(e))


app.mount("/", StaticFiles(directory="static", html=True), name="static")

# --- 3. Main Execution Block ---
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        server_header=False,  # Disables "Server: uvicorn"
        date_header=False,    # Disables "Date" header for extra stealth
        proxy_headers=True   # Important for getting real IPs if using a proxy
    )

