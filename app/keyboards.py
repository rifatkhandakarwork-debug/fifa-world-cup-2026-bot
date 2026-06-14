from __future__ import annotations

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("📅 ম্যাচ সূচি", callback_data="schedule"), InlineKeyboardButton("🔴 লাইভ ম্যাচ", callback_data="live")],
            [InlineKeyboardButton("📊 পয়েন্ট টেবিল", callback_data="standings"), InlineKeyboardButton("👥 গ্রুপ", callback_data="groups")],
            [InlineKeyboardButton("🏅 নকআউট", callback_data="knockout"), InlineKeyboardButton("🌍 ভেন্যু", callback_data="venues")],
            [InlineKeyboardButton("🥇 খেলোয়াড় পরিসংখ্যান", callback_data="players"), InlineKeyboardButton("🔔 নোটিফিকেশন", callback_data="notifications")],
            [InlineKeyboardButton("📰 সর্বশেষ খবর", callback_data="news"), InlineKeyboardButton("⭐ প্রিয় দল", callback_data="favorite")],
            [InlineKeyboardButton("❓ AI-কে জিজ্ঞেস করুন", callback_data="ask_ai")],
        ]
    )


def nav_menu(back_to: str = "home") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [[InlineKeyboardButton("⬅️ Back", callback_data=back_to), InlineKeyboardButton("🏠 Home", callback_data="home")]]
    )


def schedule_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("আজকের ম্যাচ", callback_data="schedule:today"), InlineKeyboardButton("আগামীকাল", callback_data="schedule:tomorrow")],
            [InlineKeyboardButton("Upcoming", callback_data="schedule:upcoming"), InlineKeyboardButton("Team Search", callback_data="prompt:team")],
            [InlineKeyboardButton("Group Search", callback_data="groups"), InlineKeyboardButton("Venue Search", callback_data="prompt:venue")],
            [InlineKeyboardButton("🏠 Home", callback_data="home")],
        ]
    )


def groups_menu() -> InlineKeyboardMarkup:
    rows = []
    letters = [chr(code) for code in range(ord("A"), ord("L") + 1)]
    for index in range(0, len(letters), 3):
        rows.append([InlineKeyboardButton(f"Group {letter}", callback_data=f"group:{letter}") for letter in letters[index:index + 3]])
    rows.append([InlineKeyboardButton("🏠 Home", callback_data="home")])
    return InlineKeyboardMarkup(rows)


def notifications_menu(prefs: dict[str, bool]) -> InlineKeyboardMarkup:
    labels = {
        "goal": "Goal",
        "match_start": "Match Start",
        "half_time": "Half Time",
        "full_time": "Full Time",
        "red_card": "Red Card",
        "penalty": "Penalty",
        "extra_time": "Extra Time",
        "match_result": "Match Result",
        "favorite_team": "Favorite Team",
        "all_matches": "All Matches",
    }
    rows = []
    for key, label in labels.items():
        mark = "✅" if prefs.get(key, False) else "❌"
        rows.append([InlineKeyboardButton(f"{mark} {label}", callback_data=f"notify:{key}")])
    rows.append([InlineKeyboardButton("🏠 Home", callback_data="home")])
    return InlineKeyboardMarkup(rows)


def back_menu(back_to: str = "home") -> InlineKeyboardMarkup:
    return nav_menu(back_to)
