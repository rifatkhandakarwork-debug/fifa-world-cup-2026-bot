from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import ContextTypes

from app.keyboards import main_menu
from app.services.container import Services


logger = logging.getLogger(__name__)


def services(context: ContextTypes.DEFAULT_TYPE) -> Services:
    return context.application.bot_data["services"]


async def safe_edit(update: Update, text: str, reply_markup=None) -> None:
    query = update.callback_query
    if query:
        await query.answer()
        await query.edit_message_text(text, parse_mode="HTML", reply_markup=reply_markup, disable_web_page_preview=True)
    elif update.effective_message:
        await update.effective_message.reply_text(text, parse_mode="HTML", reply_markup=reply_markup, disable_web_page_preview=True)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.exception("Unhandled bot error", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text("⚠️ Unable to fetch data.\n\nPlease try again later.")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.effective_message.reply_text("Menu থেকে option বেছে নিন অথবা /ask লিখে প্রশ্ন করুন।", reply_markup=main_menu())
