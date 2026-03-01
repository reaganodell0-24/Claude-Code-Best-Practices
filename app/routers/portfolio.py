"""Portfolio management API endpoints."""
from fastapi import APIRouter, HTTPException
from app.models import PortfolioHolding
from app.services.portfolio_manager import (
    get_holdings, add_holding, update_holding, delete_holding,
    get_portfolio_summary, get_watchlist, add_to_watchlist, remove_from_watchlist,
)

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])


@router.get("/holdings")
async def list_holdings():
    return await get_holdings()


@router.get("/summary")
async def portfolio_summary():
    return await get_portfolio_summary()


@router.post("/holdings")
async def create_holding(holding: PortfolioHolding):
    return await add_holding(holding.ticker, holding.shares, holding.avg_cost)


@router.put("/holdings/{holding_id}")
async def modify_holding(holding_id: int, holding: PortfolioHolding):
    success = await update_holding(holding_id, holding.shares, holding.avg_cost)
    if not success:
        raise HTTPException(status_code=404, detail="Holding not found")
    return {"status": "updated"}


@router.delete("/holdings/{holding_id}")
async def remove_holding(holding_id: int):
    success = await delete_holding(holding_id)
    if not success:
        raise HTTPException(status_code=404, detail="Holding not found")
    return {"status": "deleted"}


@router.get("/watchlist")
async def list_watchlist():
    return await get_watchlist()


@router.post("/watchlist/{ticker}")
async def add_watchlist(ticker: str):
    await add_to_watchlist(ticker)
    return {"status": "added", "ticker": ticker.upper()}


@router.delete("/watchlist/{ticker}")
async def remove_watchlist(ticker: str):
    success = await remove_from_watchlist(ticker)
    if not success:
        raise HTTPException(status_code=404, detail="Ticker not in watchlist")
    return {"status": "removed"}
