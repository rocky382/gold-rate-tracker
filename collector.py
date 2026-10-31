import csv
import os
from datetime import date
from playwright.sync_api import sync_playwright

CSV_FILE = "rates.csv"
URL = "https://www.joyalukkas.com/om/goldrate"


def fetch_rates():
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled", "--no-sandbox"]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        )
        page = context.new_page()
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        page.goto(URL, wait_until="domcontentloaded", timeout=45000)
        page.wait_for_selector("text=22KT GOLD RATE", timeout=30000)

        def extract_number(karat_text):
            try:
                row = page.locator(f"tr:has-text('{karat_text}') td").last
                return float(row.text_content().replace("OMR", "").strip())
            except Exception:
                return None

        r22 = extract_number("22KT")
        r24 = extract_number("24KT")
        r18 = extract_number("18KT")
        browser.close()
        return r22, r24, r18


def save_to_csv(r22, r24, r18):
    today = date.today().isoformat()
    rows = []
    exists = os.path.exists(CSV_FILE)

    if exists:
        with open(CSV_FILE, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            rows = list(reader)

    # Avoid duplicate entry for the same date
    updated = False
    for i, row in enumerate(rows):
        if row and row[0] == today:
            rows[i] = [today, r22, r24, r18]
            updated = True
            break

    if not updated:
        if not rows:
            rows.append(["date", "rate_22k", "rate_24k", "rate_18k"])
        rows.append([today, r22, r24, r18])

    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(rows)

    print(f"[{today}] Saved: 22K={r22}, 24K={r24}, 18K={r18}")


if __name__ == "__main__":
    r22, r24, r18 = fetch_rates()
    if r22:
        save_to_csv(r22, r24, r18)
    else:
        print("Scrape failed.")