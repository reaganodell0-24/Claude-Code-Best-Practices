"""Portfolio database operations and P&L calculations."""
from app.database import get_db
from app.services.data_fetcher import fetch_quote


async def get_holdings() -> list[dict]:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT id, ticker, shares, avg_cost FROM holdings ORDER BY ticker")
        rows = await cursor.fetchall()
        holdings = []
        for row in rows:
            ticker = row[1]
            shares = row[2]
            avg_cost = row[3]
            quote = fetch_quote(ticker)
            current_price = quote["price"] if quote else avg_cost
            market_value = round(shares * current_price, 2)
            cost_basis = round(shares * avg_cost, 2)
            gain_loss = round(market_value - cost_basis, 2)
            gain_loss_pct = round((gain_loss / cost_basis * 100) if cost_basis else 0, 2)
            holdings.append({
                "id": row[0],
                "ticker": ticker,
                "shares": shares,
                "avg_cost": avg_cost,
                "current_price": current_price,
                "market_value": market_value,
                "gain_loss": gain_loss,
                "gain_loss_pct": gain_loss_pct,
            })
        return holdings
    finally:
        await db.close()


async def add_holding(ticker: str, shares: float, avg_cost: float) -> dict:
    db = await get_db()
    try:
        cursor = await db.execute(
            "INSERT INTO holdings (ticker, shares, avg_cost) VALUES (?, ?, ?)",
            (ticker.upper(), shares, avg_cost),
        )
        await db.commit()
        return {"id": cursor.lastrowid, "ticker": ticker.upper(), "shares": shares, "avg_cost": avg_cost}
    finally:
        await db.close()


async def update_holding(holding_id: int, shares: float = None, avg_cost: float = None) -> bool:
    db = await get_db()
    try:
        updates = []
        params = []
        if shares is not None:
            updates.append("shares = ?")
            params.append(shares)
        if avg_cost is not None:
            updates.append("avg_cost = ?")
            params.append(avg_cost)
        if not updates:
            return False
        params.append(holding_id)
        await db.execute(f"UPDATE holdings SET {', '.join(updates)} WHERE id = ?", params)
        await db.commit()
        return True
    finally:
        await db.close()


async def delete_holding(holding_id: int) -> bool:
    db = await get_db()
    try:
        cursor = await db.execute("DELETE FROM holdings WHERE id = ?", (holding_id,))
        await db.commit()
        return cursor.rowcount > 0
    finally:
        await db.close()


async def get_portfolio_summary() -> dict:
    holdings = await get_holdings()
    total_value = sum(h["market_value"] for h in holdings)
    total_cost = sum(h["shares"] * h["avg_cost"] for h in holdings)
    total_gain = round(total_value - total_cost, 2)
    total_gain_pct = round((total_gain / total_cost * 100) if total_cost else 0, 2)
    return {
        "total_value": round(total_value, 2),
        "total_cost": round(total_cost, 2),
        "total_gain": total_gain,
        "total_gain_pct": total_gain_pct,
        "holdings": holdings,
    }


async def get_watchlist() -> list[str]:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT ticker FROM watchlist ORDER BY ticker")
        rows = await cursor.fetchall()
        return [row[0] for row in rows]
    finally:
        await db.close()


async def add_to_watchlist(ticker: str) -> bool:
    db = await get_db()
    try:
        await db.execute(
            "INSERT OR IGNORE INTO watchlist (ticker) VALUES (?)",
            (ticker.upper(),),
        )
        await db.commit()
        return True
    finally:
        await db.close()


async def remove_from_watchlist(ticker: str) -> bool:
    db = await get_db()
    try:
        cursor = await db.execute("DELETE FROM watchlist WHERE ticker = ?", (ticker.upper(),))
        await db.commit()
        return cursor.rowcount > 0
    finally:
        await db.close()
