"""Data fetcher with Alpha Vantage (primary for quotes) + yfinance (fallback & historicals)."""
import time
import yfinance as yf
import pandas as pd
from typing import Optional
import config

_cache: dict[str, tuple[float, any]] = {}

# Store ticker names from yfinance for AV quotes that lack them
_ticker_names: dict[str, str] = {}


def _cache_get(key: str, ttl: int):
    if key in _cache:
        ts, val = _cache[key]
        if time.time() - ts < ttl:
            return val
    return None


def _cache_set(key: str, val):
    _cache[key] = (time.time(), val)


def fetch_historical(ticker: str, period: str = "1y", interval: str = "1d") -> list[dict]:
    """Fetch OHLCV data — yfinance for historical (richer data, no hard rate limit)."""
    key = f"hist:{ticker}:{period}:{interval}"
    cached = _cache_get(key, config.HISTORICAL_CACHE_TTL)
    if cached is not None:
        return cached

    try:
        tk = yf.Ticker(ticker)
        df = tk.history(period=period, interval=interval)
    except Exception:
        return []

    if df is None or df.empty:
        return []

    candles = []
    for idx, row in df.iterrows():
        ts = idx
        if hasattr(ts, 'tz_localize'):
            try:
                ts = ts.tz_localize(None)
            except TypeError:
                ts = ts.tz_convert(None)

        if interval in ("1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"):
            time_val = int(ts.timestamp())
        else:
            time_val = ts.strftime("%Y-%m-%d")

        candles.append({
            "time": time_val,
            "open": round(float(row["Open"]), 2),
            "high": round(float(row["High"]), 2),
            "low": round(float(row["Low"]), 2),
            "close": round(float(row["Close"]), 2),
            "volume": int(row["Volume"]) if pd.notna(row["Volume"]) else 0,
        })

    _cache_set(key, candles)
    return candles


def fetch_quote(ticker: str) -> Optional[dict]:
    """Fetch quote — Alpha Vantage first (real-time), yfinance fallback."""
    key = f"quote:{ticker}"
    cached = _cache_get(key, config.QUOTE_CACHE_TTL)
    if cached is not None:
        return cached

    # Try Alpha Vantage first
    if config.ALPHA_VANTAGE_API_KEY:
        try:
            from app.services.alpha_vantage import fetch_av_quote
            av_quote = fetch_av_quote(ticker)
            if av_quote and av_quote.get("price"):
                # Enrich with name from yfinance if we have it cached
                if av_quote["name"] == ticker.upper() and ticker.upper() in _ticker_names:
                    av_quote["name"] = _ticker_names[ticker.upper()]
                _cache_set(key, av_quote)
                return av_quote
        except Exception:
            pass

    # Fallback to yfinance
    return _fetch_quote_yfinance(ticker)


def _fetch_quote_yfinance(ticker: str) -> Optional[dict]:
    """Fetch quote from yfinance."""
    key = f"quote:{ticker}"

    try:
        tk = yf.Ticker(ticker)
        info = tk.info
    except Exception:
        return None

    if not info:
        return None

    price = info.get("regularMarketPrice") or info.get("currentPrice")
    if not price:
        return None

    prev_close = info.get("regularMarketPreviousClose") or info.get("previousClose", price)
    change = round(price - prev_close, 2)
    change_pct = round((change / prev_close * 100) if prev_close else 0, 2)

    name = info.get("shortName") or info.get("longName", ticker.upper())
    _ticker_names[ticker.upper()] = name

    quote = {
        "ticker": ticker.upper(),
        "name": name,
        "price": round(price, 2),
        "change": change,
        "change_percent": change_pct,
        "volume": info.get("regularMarketVolume") or info.get("volume"),
        "market_cap": info.get("marketCap"),
        "source": "yfinance",
    }

    _cache_set(key, quote)
    return quote


def validate_ticker(ticker: str) -> bool:
    """Check if a ticker is valid."""
    try:
        tk = yf.Ticker(ticker)
        info = tk.info
        return bool(info and (info.get("regularMarketPrice") or info.get("currentPrice")))
    except Exception:
        return False


def search_tickers(query: str) -> list[dict]:
    """Search tickers — try Alpha Vantage first, yfinance fallback."""
    # Try Alpha Vantage
    if config.ALPHA_VANTAGE_API_KEY:
        try:
            from app.services.alpha_vantage import fetch_av_search
            results = fetch_av_search(query)
            if results:
                return results
        except Exception:
            pass

    # Fallback to yfinance
    try:
        results = yf.Search(query)
        quotes = getattr(results, "quotes", []) or []
        return [
            {
                "symbol": q.get("symbol", ""),
                "name": q.get("shortname") or q.get("longname") or q.get("shortName") or q.get("longName", ""),
                "exchange": q.get("exchange", ""),
                "type": q.get("quoteType", ""),
            }
            for q in quotes[:10]
        ]
    except Exception:
        return []
