"""Tests for the indicators service."""
import pytest
from app.services.indicators import calc_sma, calc_ema, calc_rsi, calc_macd, calc_bollinger


def test_sma():
    data = calc_sma("AAPL", length=20, period="3mo", interval="1d")
    assert len(data) > 0
    assert "time" in data[0]
    assert "value" in data[0]
    assert isinstance(data[0]["value"], float)


def test_ema():
    data = calc_ema("AAPL", length=20, period="3mo", interval="1d")
    assert len(data) > 0
    assert "value" in data[0]


def test_rsi():
    data = calc_rsi("AAPL", length=14, period="3mo", interval="1d")
    assert len(data) > 0
    for d in data:
        assert 0 <= d["value"] <= 100


def test_macd():
    data = calc_macd("AAPL", period="3mo", interval="1d")
    assert "macd" in data
    assert "signal" in data
    assert "histogram" in data
    assert len(data["macd"]) > 0


def test_bollinger():
    data = calc_bollinger("AAPL", period="3mo", interval="1d")
    assert "upper" in data
    assert "middle" in data
    assert "lower" in data
    assert len(data["upper"]) > 0
    # Upper should be above lower
    if data["upper"] and data["lower"]:
        assert data["upper"][0]["value"] > data["lower"][0]["value"]
