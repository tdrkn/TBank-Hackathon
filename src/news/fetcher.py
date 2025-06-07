import hashlib
import feedparser
import aiohttp

from .dedup import is_new_article
from ..llm.openai_runner import extract_json
from ..db.migrate import AsyncSessionLocal
from ..db import models


def sentiment_label(value: float) -> str:
    if value > 0.1:
        return "позитивная"
    if value < -0.1:
        return "негативная"
    return "нейтральная"

RSS_FEEDS = {
    "rbc_main": "https://static.feed.rbc.ru/rbc/internal/rss.rbc.ru/rbc.ru/mainnews.rss",
    "kommersant": "https://www.kommersant.ru/RSS/section-economics.xml",
    "cbr": "http://www.cbr.ru/rss/RssNews",
    "banki": "https://www.banki.ru/news/lenta/?r1=rss&r2=news",
    "finam_companies": "https://www.finam.ru/analysis/conews/rsspoint/",
    "finam_bonds": "https://bonds.finam.ru/news/today/rss.asp",
    "tass": "https://tass.com/rss/v2.xml",
    "profinance_stocks": "https://www.profinance.ru/fond.xml",
    "profinance_economy": "https://www.profinance.ru/econom.xml",
}


async def process_entry(entry) -> None:
    url_hash = hashlib.sha256(entry.link.encode()).hexdigest()
    if not await is_new_article(url_hash):
        return
    data = await extract_json(entry.summary)
    async with AsyncSessionLocal() as session:
        article = models.Article(
            ticker=data.ticker,
            url=url_hash,
            headline=entry.title,
            summary=data.summary,
            sentiment=data.sentiment,
            impact=data.impact,
            event_type=data.event_type,
        )
        session.add(article)
        await session.commit()
    print(f"{data.ticker}: {sentiment_label(data.sentiment)}")


async def fetch_all() -> None:
    async with aiohttp.ClientSession() as session:
        for url in RSS_FEEDS.values():
            async with session.get(url, timeout=30) as resp:
                text = await resp.text()
                parsed = feedparser.parse(text)
                for entry in parsed["entries"]:
                    await process_entry(entry)
