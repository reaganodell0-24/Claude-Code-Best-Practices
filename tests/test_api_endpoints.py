"""Tests for API endpoints."""
import pytest
from fastapi.testclient import TestClient
from app.main import app
import config

config.DB_PATH = "data/test_api_dashboard.db"

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Financial Analysis Dashboard" in response.text


def test_historical_endpoint():
    response = client.get("/api/market/historical/AAPL?period=1mo&interval=1d")
    assert response.status_code == 200
    data = response.json()
    assert "candles" in data
    assert len(data["candles"]) > 0


def test_quote_endpoint():
    response = client.get("/api/market/quote/AAPL")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert "price" in data


def test_search_endpoint():
    response = client.get("/api/market/search?q=Apple")
    assert response.status_code == 200
    data = response.json()
    assert "results" in data


def test_timeframes_endpoint():
    response = client.get("/api/market/timeframes")
    assert response.status_code == 200
    data = response.json()
    assert "1Y" in data["timeframes"]


def test_sma_endpoint():
    response = client.get("/api/technical/sma/AAPL?length=20&period=3mo&interval=1d")
    assert response.status_code == 200
    data = response.json()
    assert data["indicator"] == "SMA"
    assert len(data["data"]) > 0


def test_rsi_endpoint():
    response = client.get("/api/technical/rsi/AAPL?period=3mo&interval=1d")
    assert response.status_code == 200
    data = response.json()
    assert data["indicator"] == "RSI"


def test_fundamentals_endpoint():
    response = client.get("/api/fundamentals/AAPL")
    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "AAPL"
    assert "pe_ratio" in data


def test_portfolio_crud():
    # Add
    response = client.post("/api/portfolio/holdings", json={
        "ticker": "AAPL", "shares": 10, "avg_cost": 150.0,
    })
    assert response.status_code == 200
    holding_id = response.json()["id"]

    # List
    response = client.get("/api/portfolio/holdings")
    assert response.status_code == 200

    # Summary
    response = client.get("/api/portfolio/summary")
    assert response.status_code == 200

    # Delete
    response = client.delete(f"/api/portfolio/holdings/{holding_id}")
    assert response.status_code == 200


def test_invalid_ticker():
    response = client.get("/api/market/historical/INVALIDTICKER999?period=1mo&interval=1d")
    assert response.status_code == 404
