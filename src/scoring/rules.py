from datetime import datetime, timedelta
from sqlalchemy import func, select

from ..db.migrate import AsyncSessionLocal
from ..db import models
from ..brokers.tinvest import get_historic_prices

def momentum(figi: str) -> int:
    end = datetime.utcnow()
    start = end - timedelta(days=21)
    candles = get_historic_prices(figi, start, end)
    if not candles:
        return 0
    prices = [c.close for c in candles]
    sma = sum(prices[:-1]) / len(prices[:-1])
    return 1 if prices[-1] > sma else 0


async def rank_assets(session: AsyncSessionLocal) -> list[tuple[str, float]]:
    sent_7d = (
        select(
            models.Article.ticker,
            func.avg(models.Article.sentiment).label("sent")
        )
        .where(models.Article.created_at >= datetime.utcnow() - timedelta(days=7))
        .group_by(models.Article.ticker)
    )

    buzz_24h = (
        select(
            models.Article.ticker,
            func.count(models.Article.id).label("cnt")
        )
        .where(models.Article.created_at >= datetime.utcnow() - timedelta(days=1))
        .group_by(models.Article.ticker)
    )

    results = {}
    async with session() as sess:
        sent = await sess.execute(sent_7d)
        for t, val in sent.all():
            results[t] = results.get(t, 0) + 0.4 * val
        buzz = await sess.execute(buzz_24h)
        for t, cnt in buzz.all():
            results[t] = results.get(t, 0) + 0.3 * cnt
        for t in results.keys():
            results[t] += 0.3 * momentum(t)

    ranked = sorted(results.items(), key=lambda x: x[1], reverse=True)[:10]
    return ranked
