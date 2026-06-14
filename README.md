# FIFA World Cup 2026 Telegram Bot

Professional async Telegram bot for FIFA World Cup 2026.

## Features

- Inline keyboard main menu
- Official FIFA match schedule and live score source
- Bangladesh time display (`Asia/Dhaka`)
- SQLite database for users, favorites, notification preferences and cache
- Cache expiry:
  - Live matches: 30 sec
  - Matches: 5 min
  - News: 15 min
- Modular Python architecture:
  - `handlers`
  - `services`
  - `database`
  - `utils`
  - `models`
- Graceful API error handling
- Favorite team and notification preference storage
- Local AI-style question parser for schedule/live/standings queries

## Setup

Python is required. On this PC, Python is not currently available in PATH.

1. Install Python 3.12+:
   https://www.python.org/downloads/windows/

2. During install, tick:
   `Add python.exe to PATH`

3. Run:

   `D:\xampp\htdocs\tg_bot\setup-python-bot.bat`

4. Start the bot:

   `D:\xampp\htdocs\tg_bot\run-python-bot.bat`

## Cloud Deployment

PC off থাকলেও bot চালাতে Render deploy guide দেখুন:

`DEPLOY_RENDER.md`

## Configuration

`.env` already contains the bot token and FIFA API settings.

Important variables:

- `BOT_TOKEN`
- `DATABASE_PATH`
- `TIMEZONE=Asia/Dhaka`
- `FIFA_CALENDAR_URL=https://api.fifa.com/api/v3/calendar/matches`
- `FIFA_COMPETITION_ID=17`

## Official Data Source

Primary match data comes from FIFA official public API:

`https://api.fifa.com/api/v3/calendar/matches`

The bot does not hardcode match data.

## Current Limitations

Some data like complete player stats, assists, saves, cards and advanced live stats depends on FIFA making public endpoints available. The bot handles those sections gracefully and can be extended by adding a reliable paid API such as Sportmonks, API-Football, SportsDataIO or BallDontLie.
