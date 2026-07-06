# HMT Watch Stock Tracker
**by Yagna Raval** — [github.com/yagnaraval](https://github.com/yagnaraval)

A free, automated stock tracker for HMT watches that checks a specific product page every 10 minutes and sends you a Telegram message the moment your desired variant becomes available.

Built with Python, Playwright, and GitHub Actions — no server, no hosting fees, no paid APIs.

---

## Why this exists

HMT watches (especially specific color variants) go out of stock almost immediately after restocking. Manually refreshing the page is impractical. This script automates the check and notifies you instantly so you can place the order before it sells out again.

---

## How it works

1. GitHub Actions triggers `check_stock.py` on a schedule (every 10 minutes via cron)
2. Playwright launches a headless Chromium browser and loads the HMT product page
3. The script locates the Maroon color swatch by its hex color code and clicks it if not already selected
4. It confirms the selected variant label says "Maroon"
5. It checks the "Add to Cart" button — if it's enabled (not disabled), the variant is in stock
6. If in stock, it sends a Telegram message to you with the product URL
7. If still out of stock, it logs "Still out of stock" and exits silently

---

## Project structure
```
hmt-watch-tracker/
├── check_stock.py          # Main script
├── requirements.txt        # Python dependencies
└── .github/
    └── workflows/
        └── check_stock.yml # GitHub Actions workflow (cron schedule)
```
---

## Setup guide

### Step 1: Fork or clone this repo

Click **Fork** on the top right of this page to copy it to your own GitHub account.
Or clone it locally:
```bash
git clone https://github.com/yagnaraval/hmt-watch-tracker.git
cd hmt-watch-tracker
```

---

### Step 2: Create a Telegram bot

You need a Telegram bot to receive notifications. This is completely free.

1. Open Telegram and search for **@BotFather** (look for the blue verified checkmark)
2. Start a chat and send `/newbot`
3. BotFather will ask for a **name** — this is the display name of your bot, e.g. `HMT Stock Tracker`
4. Then it asks for a **username** — must be unique and end in `bot`, e.g. `yagna_hmt_tracker_bot`
5. BotFather replies with your **bot token** — it looks like this:
   7123456789:AAFxyzAbCdEfGhIjKlMnOpQrStUvWxYz

6. **Save this token** — you'll need it in Step 4

> To change the bot name later: message BotFather and send `/mybots` → select your bot → Edit Name

---

### Step 3: Get your Telegram chat ID

Your chat ID tells the bot who to send messages to (you).

1. In Telegram, search for your newly created bot by its username and open a chat with it
2. Send it any message — e.g. `hello`
3. In a browser, open this URL (replace `<YOUR_TOKEN>` with your actual bot token):
   https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates

4. You'll see a JSON response. Look for this part:
```json
   "chat": {
     "id": 123456789,
     ...
   }
```
5. That number (`123456789`) is your **chat ID** — save it

> If you see `"result": []` (empty), go back to Telegram, send another message to your bot, and refresh the URL.

---

### Step 4: Add secrets to GitHub

Your bot token and chat ID are sensitive — never hardcode them in the script. GitHub Secrets stores them securely and injects them as environment variables at runtime.

1. Go to your repo on GitHub
2. Click **Settings** (top of the repo page)
3. In the left sidebar: **Secrets and variables** → **Actions**
4. Click **New repository secret** and add the following two secrets:

| Secret name | Value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Your bot token from Step 2 |
| `TELEGRAM_CHAT_ID` | Your chat ID from Step 3 |

> These are never visible to anyone after being saved, including you. GitHub only lets you update or delete them, not view them.

---

### Step 5: Verify the product URL and variant

Open `check_stock.py` and check these two lines at the top:

```python
URL = "https://www.hmtwatches.store/product/0035cf80-48d5-4cf3-a02f-1f36b01071a5"
MAROON_COLOR_HEX = "#500404"
```

**To track a different watch model:**
- Go to the HMT website, open the product page for the watch you want
- Copy the full URL from your browser's address bar
- Replace the `URL` value with your copied URL

**To track a different color variant:**
- On the product page, right-click the color swatch you want → Inspect Element
- Look for `aria-label="Select #XXXXXX color"` — the hex code is what you need
- Replace the `MAROON_COLOR_HEX` value with your hex code

> Example: for a blue variant with hex `#007FFF`, change it to:
> ```python
> MAROON_COLOR_HEX = "#007FFF"
> ```
> Also update the confirmation check a few lines below from `"maroon"` to the color name shown on the page:
> ```python
> if selected_text != "blue":  # change "maroon" to whatever color name the page uses
> ```

---

### Step 6: Push to GitHub

If you cloned the repo and made changes locally:
```bash
git add check_stock.py
git commit -m "Update watch URL and variant"
git push
```

---

### Step 7: Enable and verify GitHub Actions

1. Go to your repo → **Actions** tab
2. If you see a prompt asking to enable workflows, click **"I understand my workflows, go ahead and enable them"**
3. In the left sidebar, click **"Check HMT Watch Stock"**
4. Click **Run workflow** → **Run workflow** to trigger a manual test run
5. Wait about 60-90 seconds, then click on the run to see logs
6. You should see either `Still out of stock` or `Notified: in stock` in the logs

> If you see errors instead, check the troubleshooting section below.

---

### Step 8: Automatic scheduling

The workflow is already configured to run automatically every 10 minutes via this cron expression in `check_stock.yml`:

```yaml
on:
  schedule:
    - cron: "*/10 * * * *"
```

**Cron format reference:**
```
* * * * *
│ │ │ │ └── Day of week (0-6, Sun=0)
│ │ │ └──── Month (1-12)
│ │ └────── Day of month (1-31)
│ └──────── Hour (0-23)
└────────── Minute (0-59)
```

Common intervals:
- Every 5 minutes: `*/5 * * * *`
- Every 15 minutes: `*/15 * * * *`
- Every hour: `0 * * * *`

> **Important:** GitHub Actions cron scheduling has a known delay — runs may fire 15-30+ minutes late during periods of high load on GitHub's servers. This is a GitHub platform limitation, not a bug in this script.

> **Also important:** GitHub automatically disables scheduled workflows after **60 days of repository inactivity** (no commits or pushes). If notifications stop, go to Actions → the workflow → click "Enable workflow", or push a small commit to reset the activity timer.

---

## Testing the notification

To verify your Telegram bot actually sends messages without waiting for a real restock, temporarily edit `main()` in `check_stock.py`:

```python
def main():
    result = check_stock()
    result = True  # TEMP: force notification test — remove after testing
```

Push this change, run the workflow manually, confirm you receive a Telegram message, then revert:

```python
def main():
    result = check_stock()
    # result = True  # removed after testing
```

Push the revert immediately.

---

## Disabling or stopping the tracker

**Temporarily disable (keeps the file, stops runs):**
- Actions tab → "Check HMT Watch Stock" → "•••" menu → "Disable workflow"

**Re-enable later:**
- Same place → "Enable workflow"

**Remove permanently:**
```bash
git rm .github/workflows/check_stock.yml
git commit -m "Remove workflow"
git push
```

---

## Troubleshooting

**`Check failed: ...` in logs**
The page didn't load correctly or the variant picker wasn't found. Could be a temporary network issue on GitHub's runner — it'll retry on the next scheduled run. If it happens consistently, the page structure may have changed.

**`Could not confirm Maroon selection`**
The color label text on the page doesn't match `"maroon"` (case-sensitive after `.lower()`). Inspect the page's selected value label and update the check in the script accordingly.

**No Telegram message received despite "Notified: in stock" in logs**
Double-check your `TELEGRAM_CHAT_ID` secret — a wrong chat ID is the most common cause. Redo Step 3 to confirm the correct value.

**Workflow not running on schedule**
Check that Actions are enabled (Settings → Actions → General → "Allow all actions"). Also confirm the workflow file is on the `main` branch (scheduled workflows only run from the default branch).

---

## Dependencies

- [Playwright](https://playwright.dev/python/) — headless browser automation
- [requests](https://docs.python-requests.org/) — HTTP client for Telegram API calls

Install locally for development:
```bash
pip install playwright requests
playwright install chromium
```

---

## Connect with me

Found this useful or have suggestions? Feel free to reach out.

- 📧 Email: [ravalyagna1010@gmail.com](mailto:ravalyagna1010@gmail.com)
- 💼 LinkedIn: [linkedin.com/in/yagna-raval](https://www.linkedin.com/in/yagna-raval)