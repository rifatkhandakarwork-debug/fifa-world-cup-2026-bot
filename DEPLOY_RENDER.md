# Render Deployment Guide

এই bot Render free web service হিসেবে deploy করা যাবে।

## 1. GitHub-এ upload

এই project folder GitHub repo-তে push করুন।

Important: `.env`, `.venv`, `*.sqlite3`, `*.log` git এ যাবে না।

## 2. Render setup

1. https://render.com এ account খুলুন।
2. `New +` চাপুন।
3. `Blueprint` select করুন।
4. GitHub repo connect করুন।
5. Render `render.yaml` detect করবে।
6. `BOT_TOKEN` environment variable দিন।

## 3. Environment variable

Render dashboard থেকে:

- `BOT_TOKEN`: Telegram BotFather token

বাকি value `render.yaml` থেকে set হবে।

## 4. Local bot বন্ধ রাখুন

Cloud bot চালু হলে local PC-এর bot বন্ধ রাখতে হবে। একই token দিয়ে একসাথে দুই জায়গায় polling করলে updates conflict করবে।

Local bot বন্ধ করতে:

```powershell
Get-CimInstance Win32_Process -Filter "name = 'python.exe'" |
  Where-Object { $_.CommandLine -like '*bot.py*' } |
  ForEach-Object { Stop-Process -Id $_.ProcessId -Force }
```

## 5. Test

Render deploy complete হলে Telegram-এ:

`/start`

## Note

Render free service sleep করতে পারে। Sleep করলে bot response late হতে পারে। 24/7 guaranteed uptime দরকার হলে paid Render/Railway/VPS ভালো।
