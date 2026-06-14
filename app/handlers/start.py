from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.handlers.common import safe_edit, services
from app.keyboards import main_menu


WELCOME = (
    "<b>🏆 FIFA World Cup 2026</b>\n\n"
    "📅 Match Schedule\n"
    "🔴 Live Matches\n"
    "📊 Standings\n\n"
    "👥 Groups\n"
    "🏅 Knockout Bracket\n"
    "🌍 Venues & Stadiums\n\n"
    "🥇 Player Statistics\n"
    "🔔 Notifications\n"
    "📰 Latest News\n\n"
    "⭐ Favorite Team\n"
    "❓ Ask AI"
)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat = update.effective_chat
    if user and chat:
        await services(context).db.upsert_user(user.id, chat.id, user.username, user.first_name)
    await safe_edit(update, WELCOME, main_menu())


async def home(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await safe_edit(update, WELCOME, main_menu())
