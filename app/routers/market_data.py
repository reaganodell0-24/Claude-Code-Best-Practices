"""Market data API endpoints."""
from fastapi import APIRouter, HTTPException, Query
from app.services.data_fetcher import fetch_historical, fetch_quote, search_tickers
import config

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/historical/{ticker}")
async def get_historical(
    ticker: str,
    period: str = Query("1y", description="Time period"),
    interval: str = Query("1d", description="Data interval"),
):
    data = fetch_historical(ticker.upper(), period, interval)
    if not data:
        raise HTTPException(status_code=404, detail=f"No data found for {ticker}")
    return {"ticker": ticker.upper(), "candles": data}


@router.get("/quote/{ticker}")
async def get_quote(ticker: str):
    quote = fetch_quote(ticker.upper())
    if not quote:
        raise HTTPException(status_code=404, detail=f"No quote found for {ticker}")
    return quote


@router.get("/search")
async def search(q: str = Query(..., min_length=1)):
    results = search_tickers(q)
    return {"results": results}


@router.get("/timeframes")
async def get_timeframes():
    return {
        "timeframes": {
            label: {"period": period, "interval": interval}
            for label, (period, interval) in config.TIMEFRAMES.items()
        }
    }
