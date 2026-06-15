# HMT Watch Stock Tracker by Yagna Raval (github: https://github.com/yagnaraval)

Automatically checks the stock status of a specific HMT watch (Maroon variant) every 10 minutes and sends a Telegram notification when it becomes available.

## How it works

- A GitHub Actions workflow runs `check_stock.py` on a schedule
- The script uses Playwright to load the product page, select the Maroon color variant, and check the "Add to Cart" button state
- If the watch is in stock, it sends a message via Telegram Bot API

## Setup

1. Create a Telegram bot via [@BotFather](https://t.me/BotFather) and get the bot token
2. Get your Telegram chat ID by messaging the bot and visiting `https://api.telegram.org/bot<TOKEN>/getUpdates`
3. Add two repository secrets under Settings → Secrets and variables → Actions:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
4. Push to `main` — the workflow runs automatically every 10 minutes

## Manual run

Go to the Actions tab → "Check HMT Watch Stock" → Run workflow