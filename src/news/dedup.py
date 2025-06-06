from sqlalchemy import select

from ..db.migrate import AsyncSessionLocal
from ..db import models


async def is_new_article(url_hash: str) -> bool:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(models.Article).where(models.Article.url == url_hash)
        )
        return result.scalar() is None
