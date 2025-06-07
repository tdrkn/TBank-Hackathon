import hashlib
import feedparser
import aiohttp

from .dedup import is_new_article
from ..llm.openai_runner import extract_json
from ..db.migrate import AsyncSessionLocal
from ..db import models
from ..config import settings


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


async def fetch_all() -> None:
    async with aiohttp.ClientSession() as session:
        for url in settings.rss_feeds_map.values():
            async with session.get(url, timeout=30) as resp:
                text = await resp.text()
                parsed = feedparser.parse(text)
                for entry in parsed["entries"]:
                    await process_entry(entry)
