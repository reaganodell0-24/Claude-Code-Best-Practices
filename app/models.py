"""Pydantic schemas for API request/response models."""
from pydantic import BaseModel
from typing import Optional


class QuoteData(BaseModel):
    ticker: str
    name: str
    price: float
    change: float
    change_percent: float
    volume: Optional[float] = None
    market_cap: Optional[float] = None


class PortfolioHolding(BaseModel):
    ticker: str
    shares: float
    avg_cost: float


class PortfolioHoldingResponse(BaseModel):
    id: int
    ticker: str
    shares: float
    avg_cost: float
    current_price: float
    market_value: float
    gain_loss: float
    gain_loss_pct: float
