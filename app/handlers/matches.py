from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.config import settings
from app.handlers.common import safe_edit, services
from app.keyboards import back_menu, schedule_menu
from app.models.entities import Match
from app.utils.formatters import live_match_card, match_line


def _matches_text(title: str, matches: list[Match]) -> str:
    if not matches:
        return f"<b>{title}</b>\n\nকোনো ম্যাচ পাওয়া যায়নি।"
    return f"<b>{title}</b>\n\n" + "\n\n".join(match_line(match, settings.timezone) for match in matches[:10])


async def schedule_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await safe_edit(update, "<b>📅 ম্যাচ সূচি</b>\n\nএকটি option বেছে নিন।", schedule_menu())


async def schedule_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    action = update.callback_query.data.split(":", 1)[1]
    svc = services(context).matches
    if action == "today":
        matches = await svc.today()
        title = "আজকের ম্যাচ"
    elif action == "tomorrow":
        matches = await svc.tomorrow()
        title = "আগামীকালের ম্যাচ"
    else:
        matches = await svc.upcoming()
        title = "Upcoming Matches"
    await safe_edit(update, _matches_text(title, matches), back_menu("schedule"))


async def live_matches(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    svc = services(context).matches
    matches = await svc.live()
    if not matches:
        await safe_edit(update, "<b>🔴 লাইভ ম্যাচ</b>\n\nএখন কোনো live match নেই।", back_menu("home"))
        return
    cards = []
    for match in matches:
        cards.append(live_match_card(match, settings.timezone, await svc.live_stats(match)))
    await safe_edit(update, "\n\n".join(cards), back_menu("home"))


async def prompt_team_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await safe_edit(
        update,
        "<b>🔎 Team Search</b>\n\nTeam-এর নাম লিখে command দিন:\n\n<code>/team Argentina</code>\n<code>/team Brazil</code>\n<code>/team Spain</code>",
        back_menu("schedule"),
    )


async def prompt_venue_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await safe_edit(
        update,
        "<b>🏟 Venue Search</b>\n\nVenue বা city লিখে command দিন:\n\n<code>/venue Houston</code>\n<code>/venue Dallas</code>\n<code>/venue Stadium</code>",
        back_menu("schedule"),
    )


async def team_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = " ".join(context.args)
    if not query:
        await update.effective_message.reply_text("ব্যবহার করুন: /team Argentina")
        return
    matches = await services(context).matches.by_team(query)
    await update.effective_message.reply_text(_matches_text(f"{query} ম্যাচ", matches), parse_mode="HTML")
