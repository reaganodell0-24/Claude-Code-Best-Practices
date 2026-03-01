"""Tests for portfolio management."""
import pytest
import asyncio
from app.database import init_db
from app.services.portfolio_manager import (
    add_holding, get_holdings, delete_holding, get_portfolio_summary,
    add_to_watchlist, get_watchlist, remove_from_watchlist,
)
import config

# Use a test database
config.DB_PATH = "data/test_dashboard.db"


@pytest.fixture(autouse=True)
def setup_db():
    asyncio.get_event_loop().run_until_complete(init_db())
    yield
    import os
    try:
        os.remove("data/test_dashboard.db")
    except OSError:
        pass


@pytest.mark.asyncio
async def test_add_and_get_holdings():
    result = await add_holding("AAPL", 10, 150.0)
    assert result["ticker"] == "AAPL"
    assert result["shares"] == 10

    holdings = await get_holdings()
    assert len(holdings) >= 1
    aapl = [h for h in holdings if h["ticker"] == "AAPL"]
    assert len(aapl) >= 1


@pytest.mark.asyncio
async def test_delete_holding():
    result = await add_holding("MSFT", 5, 300.0)
    holding_id = result["id"]
    success = await delete_holding(holding_id)
    assert success is True


@pytest.mark.asyncio
async def test_portfolio_summary():
    await add_holding("AAPL", 10, 150.0)
    summary = await get_portfolio_summary()
    assert "total_value" in summary
    assert "total_cost" in summary
    assert "holdings" in summary


@pytest.mark.asyncio
async def test_watchlist():
    await add_to_watchlist("TSLA")
    wl = await get_watchlist()
    assert "TSLA" in wl

    await remove_from_watchlist("TSLA")
    wl = await get_watchlist()
    assert "TSLA" not in wl
