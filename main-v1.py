import time
from fastapi import FastAPI, HTTPException, Query, status
from fastapi.responses import JSONResponse
import yfinance as yf

# Initialize the FastAPI app
app = FastAPI(
    title="Stock History API",
    description="An API to fetch historical stock data using yfinance."
)
print("running v1...")



@app.get(
    "/health", 
    tags=["Monitoring"], 
    summary="Perform a Health Check",
    response_description="Return HTTP Status Code 200 (OK)"
)
async def health_check():
    """
    Endpoint to check the health and uptime of the API.
    """
    
    health_data = {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "1.0.0"
    }
    
    return JSONResponse(status_code=status.HTTP_200_OK, content=health_data)


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
