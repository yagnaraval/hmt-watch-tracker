from playwright.sync_api import sync_playwright
import requests
import os
import sys

URL = "https://www.hmtwatches.store/product/0035cf80-48d5-4cf3-a02f-1f36b01071a5"  # replace with actual URL
MAROON_COLOR_HEX = "#500404"

TELEGRAM_BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
TELEGRAM_CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def send_telegram_message(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text}
    r = requests.post(url, data=payload, timeout=10)
    r.raise_for_status()


def check_stock():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
        )
        page.goto(URL, wait_until="networkidle", timeout=30000)

        try:
            # Select Maroon variant if not already selected
            maroon_swatch = page.locator(f'[aria-label="Select {MAROON_COLOR_HEX} color"]')
            maroon_swatch.wait_for(timeout=15000)

            is_pressed = maroon_swatch.get_attribute("aria-pressed")
            if is_pressed != "true":
                maroon_swatch.click()
                page.wait_for_timeout(1000)  # let UI update after click

            # Confirm selected color label says Maroon
            selected_label = page.locator('[data-testid="variantoptions-selected-value"]')
            selected_text = selected_label.inner_text().strip().lower()
            if selected_text != "maroon":
                print(f"Could not confirm Maroon selection, got: {selected_text}")
                browser.close()
                return None

            # Check Add to Cart button
            button = page.locator('[data-testid="buybuttonswidget-add-to-cart-button"]')
            button.wait_for(timeout=15000)
            is_disabled = button.get_attribute("disabled")
            text = button.inner_text()

        except Exception as e:
            print(f"Check failed: {e}")
            browser.close()
            return None

        browser.close()

        in_stock = (is_disabled is None) and ("out of stock" not in text.lower())
        return in_stock


def main():
    result = check_stock()
    #result = True # checking/testing telegram feature without hitting the website

    if result is None:
        print("Check failed, skipping")
        sys.exit(0)

    if result:
        send_telegram_message(f"🚨 MAROON HMT WATCH IN STOCK! 🚨\n{URL}")
        print("Notified: in stock")
    else:
        print("Still out of stock")


if __name__ == "__main__":
    main()