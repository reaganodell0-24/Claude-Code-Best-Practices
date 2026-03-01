# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A full-stack financial analysis dashboard for stock DCF (Discounted Cash Flow) valuation and portfolio management. FastAPI backend, vanilla JS frontend, SQLite database.

## Commands

```bash
# Run the app (serves on http://localhost:8000)
python run.py

# Run all tests
pytest

# Run a single test file
pytest tests/test_api_endpoints.py

# Run a single test function
pytest tests/test_api_endpoints.py::test_root_endpoint -v

# Install dependencies
pip install -r requirements.txt
```

No linter or formatter is configured.

## Architecture

### Request Flow

```
Browser → FastAPI (app/main.py) → Routers → Services → yfinance/Alpha Vantage APIs
                                                     → SQLite (aiosqlite)
```

### Backend Layers

**Routers** (`app/routers/`) — API endpoint definitions. Each router has a URL prefix:
- `market_data.py` → `/api/market/` — quotes, historical OHLCV, ticker search, timeframes
- `fundamentals.py` → `/api/statements/` — income, cashflow, balance sheet, key metrics
- `portfolio.py` → `/api/portfolio/` — holdings CRUD, watchlist CRUD, portfolio summary
- `valuation.py` → `/api/valuation/` — DCF with auto-derived or custom assumptions

**Services** (`app/services/`) — Business logic, called by routers:
- `data_fetcher.py` — Primary data source with in-memory TTL cache. Fetches from yfinance.
- `alpha_vantage.py` — Optional real-time quotes via Alpha Vantage API. Falls back to yfinance if key missing or rate limited.
- `fundamentals.py` — Extracts financial statements from yfinance Ticker objects.
- `portfolio_manager.py` — Async SQLite operations for holdings/watchlist, P&L calculations.
- `dcf.py` — DCF valuation engine: 5-year projections, terminal value (Gordon Growth), sensitivity matrix (WACC × terminal growth).

**Data flow for caching**: Services use a shared `_cache` dict with TTL. Cache keys follow pattern `quote:{ticker}`, `hist:{ticker}:{period}:{interval}`, etc. Quote TTL = 60s, historical TTL = 3600s.

### Frontend

Single-page app served from `GET /`. No build step.

- `app/static/js/app.js` — Main controller, ticker search, tab navigation. Global `App` object holds current state.
- `app/static/js/dcf.js` — DCF valuation UI (largest file, ~8000 lines).
- `app/static/js/statements.js` — Financial statement tables with sub-tabs.
- `app/static/js/portfolio.js` — Portfolio/watchlist management UI.
- `app/static/js/utils.js` — Shared helpers: `fetchJSON()`, formatting, debounce.

### Database

SQLite at `data/dashboard.db`. Schema initialized in `app/database.py`. Three tables: `holdings` (ticker, shares, avg_cost), `watchlist` (ticker), `portfolio_snapshots` (total_value, total_cost). All DB access is async via `aiosqlite`.

### Configuration

`config.py` loads `.env` via `python-dotenv`. Key settings: `ALPHA_VANTAGE_API_KEY`, cache TTLs, default watchlist tickers, timeframe presets mapping to yfinance period/interval params.

## Testing

Tests use `pytest` + `pytest-asyncio`. Test files create separate SQLite databases (`data/test_dashboard.db`, `data/test_api_dashboard.db`). API tests use FastAPI's `TestClient`. Note: `test_indicators.py` references `app.services.indicators` which does not exist yet.

## Incomplete Features

- `pandas-ta`, `apscheduler`, `websockets` are installed but not yet used in application code.
- Technical indicators module (`app/services/indicators`) is planned but not implemented.
