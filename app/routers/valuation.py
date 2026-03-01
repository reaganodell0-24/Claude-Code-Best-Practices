"""DCF valuation API endpoints."""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.fundamentals import fetch_dcf_defaults
from app.services.dcf import run_dcf

router = APIRouter(prefix="/api/valuation", tags=["valuation"])


class DCFAssumptions(BaseModel):
    revenue_growth: Optional[float] = None
    operating_margin: Optional[float] = None
    tax_rate: Optional[float] = None
    capex_pct_revenue: Optional[float] = None
    da_pct_revenue: Optional[float] = None
    wacc: Optional[float] = None
    terminal_growth: Optional[float] = None
    projection_years: Optional[int] = None


@router.get("/dcf/{ticker}")
async def get_dcf_defaults(ticker: str):
    """Get DCF with default assumptions derived from real data."""
    defaults = fetch_dcf_defaults(ticker.upper())
    if not defaults or not defaults.get("latest_revenue"):
        raise HTTPException(status_code=404, detail=f"Insufficient data to run DCF for {ticker}")

    result = run_dcf(
        latest_revenue=defaults["latest_revenue"],
        revenue_growth=defaults["revenue_growth"],
        operating_margin=defaults["operating_margin"],
        tax_rate=defaults["tax_rate"],
        capex_pct_revenue=defaults["capex_pct_revenue"],
        da_pct_revenue=defaults["da_pct_revenue"],
        wacc=defaults["wacc"],
        terminal_growth=defaults["terminal_growth"],
        projection_years=defaults["projection_years"],
        shares_outstanding=defaults.get("shares_outstanding", 1),
        net_debt=defaults.get("net_debt", 0),
        cash=defaults.get("cash", 0),
    )
    result["assumptions"] = {
        "revenue_growth": defaults["revenue_growth"],
        "operating_margin": defaults["operating_margin"],
        "tax_rate": defaults["tax_rate"],
        "capex_pct_revenue": defaults["capex_pct_revenue"],
        "da_pct_revenue": defaults["da_pct_revenue"],
        "wacc": defaults["wacc"],
        "terminal_growth": defaults["terminal_growth"],
        "projection_years": defaults["projection_years"],
        "latest_revenue": defaults["latest_revenue"],
    }
    result["current_price"] = defaults.get("current_price")
    return result


@router.post("/dcf/{ticker}")
async def run_custom_dcf(ticker: str, assumptions: DCFAssumptions):
    """Run DCF with user-customized assumptions."""
    defaults = fetch_dcf_defaults(ticker.upper())
    if not defaults or not defaults.get("latest_revenue"):
        raise HTTPException(status_code=404, detail=f"Insufficient data to run DCF for {ticker}")

    # Merge user assumptions over defaults
    params = {
        "latest_revenue": defaults["latest_revenue"],
        "revenue_growth": assumptions.revenue_growth if assumptions.revenue_growth is not None else defaults["revenue_growth"],
        "operating_margin": assumptions.operating_margin if assumptions.operating_margin is not None else defaults["operating_margin"],
        "tax_rate": assumptions.tax_rate if assumptions.tax_rate is not None else defaults["tax_rate"],
        "capex_pct_revenue": assumptions.capex_pct_revenue if assumptions.capex_pct_revenue is not None else defaults["capex_pct_revenue"],
        "da_pct_revenue": assumptions.da_pct_revenue if assumptions.da_pct_revenue is not None else defaults["da_pct_revenue"],
        "wacc": assumptions.wacc if assumptions.wacc is not None else defaults["wacc"],
        "terminal_growth": assumptions.terminal_growth if assumptions.terminal_growth is not None else defaults["terminal_growth"],
        "projection_years": assumptions.projection_years if assumptions.projection_years is not None else defaults["projection_years"],
        "shares_outstanding": defaults.get("shares_outstanding", 1),
        "net_debt": defaults.get("net_debt", 0),
        "cash": defaults.get("cash", 0),
    }

    result = run_dcf(**params)
    result["assumptions"] = {k: v for k, v in params.items() if k not in ("shares_outstanding", "net_debt", "cash")}
    result["current_price"] = defaults.get("current_price")
    return result
