"""DCF (Discounted Cash Flow) valuation engine."""


def run_dcf(
    latest_revenue: float,
    revenue_growth: float,
    operating_margin: float,
    tax_rate: float,
    capex_pct_revenue: float,
    da_pct_revenue: float,
    wacc: float,
    terminal_growth: float,
    projection_years: int,
    shares_outstanding: float,
    net_debt: float,
    cash: float,
) -> dict:
    """Run a full DCF valuation and return projections, fair value, and sensitivity."""
    projections = []
    revenue = latest_revenue

    for year in range(1, projection_years + 1):
        revenue = revenue * (1 + revenue_growth)
        ebit = revenue * operating_margin
        da = revenue * da_pct_revenue
        ebitda = ebit + da
        nopat = ebit * (1 - tax_rate)
        capex = revenue * capex_pct_revenue
        fcf = nopat + da - capex

        discount_factor = 1 / ((1 + wacc) ** year)

        projections.append({
            "year": year,
            "revenue": round(revenue, 2),
            "ebit": round(ebit, 2),
            "ebitda": round(ebitda, 2),
            "nopat": round(nopat, 2),
            "da": round(da, 2),
            "capex": round(capex, 2),
            "fcf": round(fcf, 2),
            "discount_factor": round(discount_factor, 4),
            "pv_fcf": round(fcf * discount_factor, 2),
        })

    # Terminal value (Gordon Growth Model)
    terminal_fcf = projections[-1]["fcf"] * (1 + terminal_growth)
    terminal_value = terminal_fcf / (wacc - terminal_growth) if wacc > terminal_growth else 0
    terminal_pv = terminal_value / ((1 + wacc) ** projection_years)

    # Sum of discounted FCFs
    sum_pv_fcf = sum(p["pv_fcf"] for p in projections)

    # Enterprise value
    enterprise_value = sum_pv_fcf + terminal_pv

    # Equity value
    equity_value = enterprise_value - net_debt

    # Fair value per share
    fair_value = equity_value / shares_outstanding if shares_outstanding else 0

    # Sensitivity table: WACC vs terminal growth
    sensitivity = _build_sensitivity(
        projections=projections,
        projection_years=projection_years,
        net_debt=net_debt,
        shares_outstanding=shares_outstanding,
    )

    return {
        "projections": projections,
        "terminal_value": round(terminal_value, 2),
        "terminal_pv": round(terminal_pv, 2),
        "sum_pv_fcf": round(sum_pv_fcf, 2),
        "enterprise_value": round(enterprise_value, 2),
        "net_debt": round(net_debt, 2),
        "equity_value": round(equity_value, 2),
        "shares_outstanding": shares_outstanding,
        "fair_value": round(fair_value, 2),
        "sensitivity": sensitivity,
    }


def _build_sensitivity(
    projections: list,
    projection_years: int,
    net_debt: float,
    shares_outstanding: float,
) -> dict:
    """Build sensitivity matrix: WACC (rows) x terminal growth (cols)."""
    wacc_range = [0.08, 0.09, 0.10, 0.11, 0.12]
    tg_range = [0.01, 0.02, 0.025, 0.03, 0.04]

    last_fcf = projections[-1]["fcf"]
    matrix = []

    for w in wacc_range:
        row = []
        # Re-discount FCFs at this WACC
        sum_pv = sum(p["fcf"] / ((1 + w) ** p["year"]) for p in projections)
        for tg in tg_range:
            if w <= tg:
                row.append(None)
                continue
            tv_fcf = last_fcf * (1 + tg)
            tv = tv_fcf / (w - tg)
            tv_pv = tv / ((1 + w) ** projection_years)
            ev = sum_pv + tv_pv
            eq = ev - net_debt
            fv = eq / shares_outstanding if shares_outstanding else 0
            row.append(round(fv, 2))
        matrix.append(row)

    return {
        "wacc_values": [round(w * 100, 1) for w in wacc_range],
        "terminal_growth_values": [round(tg * 100, 1) for tg in tg_range],
        "matrix": matrix,
    }
