"""Financial statements API endpoints."""
from fastapi import APIRouter, HTTPException, Query
from app.services.fundamentals import (
    fetch_income_statement, fetch_cashflow, fetch_balance_sheet, fetch_key_metrics,
)

router = APIRouter(prefix="/api/statements", tags=["statements"])


@router.get("/{ticker}/income")
async def get_income_statement(ticker: str, freq: str = Query("annual", pattern="^(annual|quarterly)$")):
    data = fetch_income_statement(ticker.upper(), freq)
    if not data or not data.get("data"):
        raise HTTPException(status_code=404, detail=f"No income statement data for {ticker}")
    return data


@router.get("/{ticker}/cashflow")
async def get_cashflow(ticker: str, freq: str = Query("annual", pattern="^(annual|quarterly)$")):
    data = fetch_cashflow(ticker.upper(), freq)
    if not data or not data.get("data"):
        raise HTTPException(status_code=404, detail=f"No cash flow data for {ticker}")
    return data


@router.get("/{ticker}/balance-sheet")
async def get_balance_sheet(ticker: str, freq: str = Query("annual", pattern="^(annual|quarterly)$")):
    data = fetch_balance_sheet(ticker.upper(), freq)
    if not data or not data.get("data"):
        raise HTTPException(status_code=404, detail=f"No balance sheet data for {ticker}")
    return data


@router.get("/{ticker}/metrics")
async def get_key_metrics(ticker: str):
    data = fetch_key_metrics(ticker.upper())
    if not data:
        raise HTTPException(status_code=404, detail=f"No metrics for {ticker}")
    return data
