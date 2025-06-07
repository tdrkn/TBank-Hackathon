from __future__ import annotations

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from sqlalchemy import select

from ..db.migrate import AsyncSessionLocal
from ..db import models
from ..news.fetcher import fetch_all
from ..scoring.rules import rank_assets


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    async with AsyncSessionLocal() as session:
        user = models.User(telegram_id=update.effective_user.id)
        session.add(user)
        await session.commit()
    await update.message.reply_text("Привет! Используй /help для списка команд.")


async def subscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Укажите тикер")
        return
    ticker = context.args[0].upper()
    async with AsyncSessionLocal() as session:
        user = await session.get(models.User, update.effective_user.id)
        if user:
            sub = models.Subscription(user_id=user.id, ticker=ticker)
            session.add(sub)
            await session.commit()
    await update.message.reply_text(f"Подписка на {ticker} оформлена")


async def unsubscribe(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Укажите тикер")
        return
    ticker = context.args[0].upper()
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(models.Subscription).where(
                models.Subscription.ticker == ticker,
                models.Subscription.user_id == update.effective_user.id,
            )
        )
        sub = result.scalar_one_or_none()
        if sub:
            await session.delete(sub)
            await session.commit()
    await update.message.reply_text(f"Подписка на {ticker} отменена")


async def digest(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await fetch_all()
    await update.message.reply_text("Дайджест обновлен")


async def rank(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    ranked = await rank_assets(AsyncSessionLocal)
    lines = [f"{t}: {s:.2f}" for t, s in ranked[:3]]
    await update.message.reply_text("\n".join(lines))


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "/start /subscribe /unsubscribe /digest /rank /help"
    )


def setup(application: Application) -> None:
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("subscribe", subscribe))
    application.add_handler(CommandHandler("unsubscribe", unsubscribe))
    application.add_handler(CommandHandler("digest", digest))
    application.add_handler(CommandHandler("rank", rank))
    application.add_handler(CommandHandler("help", help_command))
