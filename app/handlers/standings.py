from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from app.handlers.common import safe_edit, services
from app.keyboards import back_menu, groups_menu
from app.utils.formatters import standings_table


async def standings(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    groups = await services(context).standings.all_groups()
    if not groups:
        await safe_edit(update, "⚠️ পয়েন্ট টেবিল এখনো পাওয়া যায়নি।", back_menu("home"))
        return

    parts: list[str] = []
    total = 0
    for group, rows in groups.items():
        block = f"<b>{group}</b>\n{standings_table(rows)}"
        if total + len(block) > 3600:
            parts.append("আরও group দেখতে Groups menu থেকে single group খুলুন।")
            break
        parts.append(block)
        total += len(block)
    await safe_edit(update, "\n\n".join(parts), back_menu("home"))


async def groups(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await safe_edit(update, "<b>👥 গ্রুপ</b>\n\nএকটি group বেছে নিন।", groups_menu())


async def group_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    letter = update.callback_query.data.split(":", 1)[1]
    rows = await services(context).standings.group(letter)
    await safe_edit(update, f"<b>Group {letter}</b>\n\n{standings_table(rows)}", back_menu("groups"))
