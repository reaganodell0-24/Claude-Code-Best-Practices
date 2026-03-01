"""Financial statement extraction from yfinance."""
import yfinance as yf
import pandas as pd
from app.services.data_fetcher import _cache_get, _cache_set
import config


def _safe(val):
    """Return None for NaN/missing values, else native Python type."""
    if val is None:
        return None
    if isinstance(val, float) and pd.isna(val):
        return None
    if isinstance(val, (pd.Timestamp,)):
        return val.strftime("%Y-%m-%d")
    try:
        return float(val)
    except (TypeError, ValueError):
        return None


def _df_to_dict(df: pd.DataFrame) -> dict:
    """Convert a yfinance statement DataFrame to {period: {line_item: value}}."""
    if df is None or df.empty:
        return {}
    result = {}
    for col in df.columns:
        period_key = col.strftime("%Y-%m-%d") if hasattr(col, "strftime") else str(col)
        items = {}
        for row_label in df.index:
            items[str(row_label)] = _safe(df.loc[row_label, col])
        result[period_key] = items
    return result


def fetch_income_statement(ticker: str, freq: str = "annual") -> dict:
    key = f"income:{ticker}:{freq}"
    cached = _cache_get(key, config.HISTORICAL_CACHE_TTL)
    if cached is not None:
        return cached

    tk = yf.Ticker(ticker)
    df = tk.quarterly_income_stmt if freq == "quarterly" else tk.income_stmt
    result = {"ticker": ticker.upper(), "frequency": freq, "data": _df_to_dict(df)}
    _cache_set(key, result)
    return result


def fetch_cashflow(ticker: str, freq: str = "annual") -> dict:
    key = f"cashflow:{ticker}:{freq}"
    cached = _cache_get(key, config.HISTORICAL_CACHE_TTL)
    if cached is not None:
        return cached

    tk = yf.Ticker(ticker)
    df = tk.quarterly_cashflow if freq == "quarterly" else tk.cashflow
    result = {"ticker": ticker.upper(), "frequency": freq, "data": _df_to_dict(df)}
    _cache_set(key, result)
    return result


def fetch_balance_sheet(ticker: str, freq: str = "annual") -> dict:
    key = f"balance_sheet:{ticker}:{freq}"
    cached = _cache_get(key, config.HISTORICAL_CACHE_TTL)
    if cached is not None:
        return cached

    tk = yf.Ticker(ticker)
    df = tk.quarterly_balance_sheet if freq == "quarterly" else tk.balance_sheet
    result = {"ticker": ticker.upper(), "frequency": freq, "data": _df_to_dict(df)}
    _cache_set(key, result)
    return result


def fetch_key_metrics(ticker: str) -> dict:
    key = f"key_metrics:{ticker}"
    cached = _cache_get(key, config.HISTORICAL_CACHE_TTL)
    if cached is not None:
        return cached

    tk = yf.Ticker(ticker)
    info = tk.info or {}

    def g(k):
        v = info.get(k)
        if v is not None and not (isinstance(v, float) and pd.isna(v)):
            return v
        return None

    result = {
        "ticker": ticker.upper(),
        "name": g("shortName") or g("longName"),
        "sector": g("sector"),
        "industry": g("industry"),
        "market_cap": g("marketCap"),
        "shares_outstanding": g("sharesOutstanding"),
        "beta": g("beta"),
        "pe_ratio": g("trailingPE"),
        "forward_pe": g("forwardPE"),
        "eps": g("trailingEps"),
        "dividend_yield": g("dividendYield"),
        "revenue": g("totalRevenue"),
        "revenue_growth": g("revenueGrowth"),
        "profit_margin": g("profitMargins"),
        "operating_margin": g("operatingMargins"),
        "debt_to_equity": g("debtToEquity"),
        "roe": g("returnOnEquity"),
        "current_price": g("regularMarketPrice") or g("currentPrice"),
        "target_mean": g("targetMeanPrice"),
        "target_low": g("targetLowPrice"),
        "target_high": g("targetHighPrice"),
        "recommendation": g("recommendationKey"),
    }
    _cache_set(key, result)
    return result


def fetch_dcf_defaults(ticker: str) -> dict:
    """Extract smart defaults for DCF assumptions from yfinance data."""
    key = f"dcf_defaults:{ticker}"
    cached = _cache_get(key, config.HISTORICAL_CACHE_TTL)
    if cached is not None:
        return cached

    tk = yf.Ticker(ticker)
    info = tk.info or {}

    # Get latest income statement for margins
    inc = tk.income_stmt
    cf = tk.cashflow
    bs = tk.balance_sheet

    defaults = {
        "ticker": ticker.upper(),
        "shares_outstanding": info.get("sharesOutstanding"),
        "current_price": info.get("regularMarketPrice") or info.get("currentPrice"),
        "revenue_growth": info.get("revenueGrowth") or 0.10,
        "operating_margin": info.get("operatingMargins") or 0.15,
        "tax_rate": 0.21,
        "capex_pct_revenue": 0.05,
        "da_pct_revenue": 0.03,
        "wacc": 0.10,
        "terminal_growth": 0.025,
        "projection_years": 5,
    }

    # Derive tax rate from income statement
    if inc is not None and not inc.empty:
        latest = inc.iloc[:, 0]
        pretax = _safe(latest.get("Pretax Income"))
        tax_prov = _safe(latest.get("Tax Provision"))
        if pretax and tax_prov and pretax > 0:
            defaults["tax_rate"] = round(tax_prov / pretax, 4)

        # Latest revenue for projections
        revenue = _safe(latest.get("Total Revenue"))
        if revenue:
            defaults["latest_revenue"] = revenue

        # D&A from income statement
        da = _safe(latest.get("Reconciled Depreciation"))
        if da and revenue and revenue > 0:
            defaults["da_pct_revenue"] = round(abs(da) / revenue, 4)

    # CapEx from cash flow
    if cf is not None and not cf.empty:
        latest_cf = cf.iloc[:, 0]
        capex = _safe(latest_cf.get("Capital Expenditure"))
        revenue = defaults.get("latest_revenue")
        if capex and revenue and revenue > 0:
            defaults["capex_pct_revenue"] = round(abs(capex) / revenue, 4)

    # Net debt from balance sheet
    if bs is not None and not bs.empty:
        latest_bs = bs.iloc[:, 0]
        total_debt = _safe(latest_bs.get("Total Debt")) or 0
        cash = _safe(latest_bs.get("Cash And Cash Equivalents")) or 0
        defaults["total_debt"] = total_debt
        defaults["cash"] = cash
        defaults["net_debt"] = total_debt - cash

    _cache_set(key, defaults)
    return defaults
