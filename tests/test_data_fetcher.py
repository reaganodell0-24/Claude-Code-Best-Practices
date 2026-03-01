"""Tests for the data fetcher service."""
import pytest
from app.services.data_fetcher import fetch_historical, fetch_quote, validate_ticker, search_tickers


def test_fetch_historical_valid_ticker():
    data = fetch_historical("AAPL", period="1mo", interval="1d")
    assert len(data) > 0
    candle = data[0]
    assert "time" in candle
    assert "open" in candle
    assert "high" in candle
    assert "low" in candle
    assert "close" in candle
    assert "volume" in candle


def test_fetch_historical_invalid_ticker():
    data = fetch_historical("INVALIDTICKER999", period="1mo", interval="1d")
    assert data == []


def test_fetch_quote_valid_ticker():
    quote = fetch_quote("AAPL")
    assert quote is not None
    assert quote["ticker"] == "AAPL"
    assert "price" in quote
    assert "change" in quote
    assert "change_percent" in quote
    assert quote["price"] > 0


def test_fetch_quote_has_name():
    quote = fetch_quote("MSFT")
    assert quote is not None
    assert quote["name"] != ""


def test_search_tickers():
    results = search_tickers("Apple")
    assert isinstance(results, list)
    if len(results) > 0:
        assert "symbol" in results[0]
        assert "name" in results[0]
