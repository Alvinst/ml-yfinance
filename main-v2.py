import json
from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from enum import Enum
import yfinance as yf

app = FastAPI()

class Period(str, Enum):
    p1d = "1d"
    p5d = "5d"
    p1mo = "1mo"
    p1y = "1y"
    # ... add others as needed

@app.get("/stock/{ticker}")
async def get_and_save_stock_data(
    ticker: str, 
    period: Period = Query(default=Period.p1mo)
):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period=period.value)
        
        if hist.empty:
            raise HTTPException(status_code=404, detail="Data not found")

        # Process data
        hist_data = hist.reset_index()
        hist_data['Date'] = hist_data['Date'].dt.strftime('%Y-%m-%d')
        data_list = hist_data.to_dict(orient="records")

        # 1. Create the filename
        # Format: MSFT_1mo_20260311.json
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"{ticker.upper()}_{period.value}_{date_str}.json"

        # 2. Save to file
        with open(filename, "w") as f:
            json.dump(data_list, f, indent=4)

        # 3. Return response
        return {
            "status": "Saved successfully",
            "filename": filename,
            "ticker": ticker.upper(),
            "data": data_list
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
