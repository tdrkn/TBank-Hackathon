import asyncio

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.ext import Application

from .config import settings
from .db.migrate import migrate
from .news.fetcher import fetch_all
from .bot import handlers


async def main() -> None:
    await migrate()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(fetch_all, "interval", minutes=30)
    scheduler.start()

    application = Application.builder().token(
        settings.telegram_token.get_secret_value()
    ).build()
    handlers.setup(application)

    print("Bot started")
    await application.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
