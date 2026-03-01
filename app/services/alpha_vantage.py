"""Alpha Vantage API client for real-time quotes and intraday data."""
import requests
from typing import Optional
import config
from app.services.data_fetcher import _cache_get, _cache_set

_AV_KEY = config.ALPHA_VANTAGE_API_KEY
_AV_URL = config.ALPHA_VANTAGE_BASE_URL


def _av_request(params: dict) -> Optional[dict]:
    """Make a request to Alpha Vantage API."""
    if not _AV_KEY:
        return None
    params["apikey"] = _AV_KEY
    try:
        r = requests.get(_AV_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        if "Error Message" in data or "Note" in data:
            return None
        return data
    except Exception:
        return None


def fetch_av_quote(ticker: str) -> Optional[dict]:
    """Fetch real-time quote from Alpha Vantage GLOBAL_QUOTE endpoint."""
    key = f"av_quote:{ticker}"
    cached = _cache_get(key, 30)  # 30s cache for real-time
    if cached is not None:
        return cached

    data = _av_request({
        "function": "GLOBAL_QUOTE",
        "symbol": ticker,
    })

    if not data or "Global Quote" not in data:
        return None

    gq = data["Global Quote"]
    if not gq or "05. price" not in gq:
        return None

    price = float(gq.get("05. price", 0))
    prev_close = float(gq.get("08. previous close", price))
    change = float(gq.get("09. change", 0))
    change_pct_str = gq.get("10. change percent", "0%").replace("%", "")
    change_pct = float(change_pct_str) if change_pct_str else 0
    volume = int(gq.get("06. volume", 0))

    quote = {
        "ticker": ticker.upper(),
        "name": ticker.upper(),  # AV GLOBAL_QUOTE doesn't return name
        "price": round(price, 2),
        "change": round(change, 2),
        "change_percent": round(change_pct, 2),
        "volume": volume,
        "market_cap": None,
        "source": "alpha_vantage",
    }

    _cache_set(key, quote)
    return quote


def fetch_av_intraday(ticker: str, interval: str = "5min") -> list[dict]:
    """Fetch intraday OHLCV from Alpha Vantage."""
    key = f"av_intraday:{ticker}:{interval}"
    cached = _cache_get(key, 60)
    if cached is not None:
        return cached

    data = _av_request({
        "function": "TIME_SERIES_INTRADAY",
        "symbol": ticker,
        "interval": interval,
        "outputsize": "compact",
    })

    ts_key = f"Time Series ({interval})"
    if not data or ts_key not in data:
        return []

    candles = []
    for timestamp, values in sorted(data[ts_key].items()):
        candles.append({
            "time": timestamp,
            "open": round(float(values["1. open"]), 2),
            "high": round(float(values["2. high"]), 2),
            "low": round(float(values["3. low"]), 2),
            "close": round(float(values["4. close"]), 2),
            "volume": int(values["5. volume"]),
        })

    _cache_set(key, candles)
    return candles


def fetch_av_search(query: str) -> list[dict]:
    """Search tickers via Alpha Vantage SYMBOL_SEARCH."""
    data = _av_request({
        "function": "SYMBOL_SEARCH",
        "keywords": query,
    })

    if not data or "bestMatches" not in data:
        return []

    return [
        {
            "symbol": m.get("1. symbol", ""),
            "name": m.get("2. name", ""),
            "type": m.get("3. type", ""),
            "region": m.get("4. region", ""),
        }
        for m in data["bestMatches"][:10]
    ]
