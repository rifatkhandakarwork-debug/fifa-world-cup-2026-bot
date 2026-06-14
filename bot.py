from __future__ import annotations

import asyncio
import sys

from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

from app.config import settings
from app.handlers.common import error_handler, unknown
from app.handlers.matches import (
    live_matches,
    prompt_team_search,
    prompt_venue_search,
    schedule_callback,
    schedule_menu_handler,
    team_search,
)
from app.handlers.more import (
    ask_ai,
    ask_ai_prompt,
    favorite,
    knockout,
    news,
    notifications,
    players,
    set_favorite,
    team_details,
    toggle_notification,
    venue_search,
    venues,
)
from app.handlers.standings import group_details, groups, standings
from app.handlers.start import home, start
from app.logging_config import setup_logging
from app.services.container import build_services


async def post_init(application: Application) -> None:
    await application.bot_data["services"].db.init()


def build_app() -> Application:
    if not settings.bot_token:
        raise RuntimeError("BOT_TOKEN is missing. Copy .env.example to .env and set BOT_TOKEN.")

    services = build_services(settings)
    application = Application.builder().token(settings.bot_token).post_init(post_init).build()
    application.bot_data["services"] = services

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("team", team_details))
    application.add_handler(CommandHandler("venue", venue_search))
    application.add_handler(CommandHandler("favorite", set_favorite))
    application.add_handler(CommandHandler("ask", ask_ai))
    application.add_handler(CommandHandler("live", live_matches))
    application.add_handler(CommandHandler("schedule", schedule_menu_handler))

    application.add_handler(CallbackQueryHandler(home, pattern="^home$"))
    application.add_handler(CallbackQueryHandler(schedule_menu_handler, pattern="^schedule$"))
    application.add_handler(CallbackQueryHandler(schedule_callback, pattern="^schedule:"))
    application.add_handler(CallbackQueryHandler(prompt_team_search, pattern="^prompt:team$"))
    application.add_handler(CallbackQueryHandler(prompt_venue_search, pattern="^prompt:venue$"))
    application.add_handler(CallbackQueryHandler(live_matches, pattern="^live$"))
    application.add_handler(CallbackQueryHandler(standings, pattern="^standings$"))
    application.add_handler(CallbackQueryHandler(groups, pattern="^groups$"))
    application.add_handler(CallbackQueryHandler(group_details, pattern="^group:"))
    application.add_handler(CallbackQueryHandler(knockout, pattern="^knockout$"))
    application.add_handler(CallbackQueryHandler(venues, pattern="^venues$"))
    application.add_handler(CallbackQueryHandler(players, pattern="^players$"))
    application.add_handler(CallbackQueryHandler(news, pattern="^news$"))
    application.add_handler(CallbackQueryHandler(notifications, pattern="^notifications$"))
    application.add_handler(CallbackQueryHandler(toggle_notification, pattern="^notify:"))
    application.add_handler(CallbackQueryHandler(favorite, pattern="^favorite$"))
    application.add_handler(CallbackQueryHandler(ask_ai_prompt, pattern="^ask_ai$"))

    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown))
    application.add_error_handler(error_handler)
    return application


def main() -> None:
    setup_logging()
    asyncio.set_event_loop(asyncio.new_event_loop())
    app = build_app()
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
