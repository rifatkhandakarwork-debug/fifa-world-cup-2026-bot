from __future__ import annotations

import html

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from app.config import settings
from app.handlers.common import safe_edit, services
from app.keyboards import back_menu, notifications_menu
from app.utils.formatters import match_line, news_card


async def knockout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await safe_edit(
        update,
        "<b>🏅 নকআউট ব্র্যাকেট</b>\n\nRound of 32, Round of 16, Quarter Final, Semi Final, Third Place Match এবং Final data publish হলে এখানে auto দেখাবে।",
        back_menu("home"),
    )


async def venues(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    venue_list = await services(context).venues.list_venues()
    if not venue_list:
        await safe_edit(update, "⚠️ Venue data পাওয়া যায়নি।", back_menu("home"))
        return
    text = "<b>🌍 ভেন্যু ও স্টেডিয়াম</b>\n\n"
    for venue in venue_list[:10]:
        text += (
            f"<b>{html.escape(venue['name'])}</b>\n"
            f"{html.escape(venue['city'])}, {html.escape(venue['country'])}\n"
            f"ম্যাচ: {len(venue['matches'])}\n"
            f"Map: {html.escape(venue['map'])}\n\n"
        )
    await safe_edit(update, text, back_menu("home"))


async def venue_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = " ".join(context.args).strip()
    if not query:
        await update.effective_message.reply_text("ব্যবহার করুন: /venue Houston")
        return
    matches = await services(context).matches.by_venue(query)
    if not matches:
        await update.effective_message.reply_text("এই venue/city দিয়ে কোনো ম্যাচ পাওয়া যায়নি।")
        return
    text = f"<b>{html.escape(query)} venue/city ম্যাচ</b>\n\n"
    text += "\n\n".join(match_line(match, settings.timezone) for match in matches[:10])
    await update.effective_message.reply_text(text, parse_mode="HTML")


async def players(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await safe_edit(update, await services(context).players.unavailable_message(), back_menu("home"))


async def news(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    items = await services(context).news.latest()
    if not items:
        await safe_edit(update, "⚠️ সর্বশেষ খবর পাওয়া যায়নি।", back_menu("home"))
        return
    buttons = [[InlineKeyboardButton("Read More", url=item.url)] for item in items[:3] if item.url]
    buttons.append([InlineKeyboardButton("⬅️ Back", callback_data="home"), InlineKeyboardButton("🏠 Home", callback_data="home")])
    await safe_edit(update, "\n\n".join(news_card(item) for item in items[:3]), InlineKeyboardMarkup(buttons))


async def notifications(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    prefs = await services(context).notifications.preferences(update.effective_user.id)
    await safe_edit(update, "<b>🔔 নোটিফিকেশন</b>\n\nযে alert দরকার সেটি on/off করুন।", notifications_menu(prefs))


async def toggle_notification(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    pref = update.callback_query.data.split(":", 1)[1]
    await services(context).notifications.toggle(update.effective_user.id, pref)
    await notifications(update, context)


async def favorite(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    team = await services(context).db.get_favorite_team(update.effective_user.id)
    text = "<b>⭐ প্রিয় দল</b>\n\n"
    text += f"বর্তমান প্রিয় দল: <b>{html.escape(team)}</b>\n\n" if team else "এখনো প্রিয় দল set করা হয়নি।\n\n"
    text += "Set করতে লিখুন: /favorite Argentina"
    await safe_edit(update, text, back_menu("home"))


async def set_favorite(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    team = " ".join(context.args).strip()
    if not team:
        await update.effective_message.reply_text("ব্যবহার করুন: /favorite Argentina")
        return
    await services(context).db.set_favorite_team(update.effective_user.id, team)
    await update.effective_message.reply_text(f"✅ প্রিয় দল set করা হয়েছে: {html.escape(team)}", parse_mode="HTML")


async def ask_ai_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await safe_edit(update, "<b>❓ AI-কে জিজ্ঞেস করুন</b>\n\n/ask লিখে প্রশ্ন করুন।\nExample: /ask show today's matches", back_menu("home"))


async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    question = " ".join(context.args).strip()
    if not question:
        await update.effective_message.reply_text("ব্যবহার করুন: /ask Who is playing today?")
        return
    answer = await services(context).ai.answer(question)
    await update.effective_message.reply_text(answer, parse_mode="HTML")


async def team_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = " ".join(context.args).strip()
    if not query:
        await update.effective_message.reply_text("ব্যবহার করুন: /team Argentina")
        return
    data = await services(context).teams.search(query)
    if not data:
        await update.effective_message.reply_text("⚠️ Team data পাওয়া যায়নি।")
        return
    upcoming = "\n\n".join(match_line(match, settings.timezone) for match in data["upcoming_matches"])
    recent = "\n\n".join(match_line(match, settings.timezone) for match in data["recent_matches"])
    await update.effective_message.reply_text(
        f"<b>{html.escape(data['name'])}</b>\n\n<b>Upcoming Matches</b>\n{upcoming or 'None'}\n\n<b>Recent Matches</b>\n{recent or 'None'}",
        parse_mode="HTML",
    )
