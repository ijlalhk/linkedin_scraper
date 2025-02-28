from playwright.sync_api import sync_playwright
import json
from linkedin_scraper.config import LINKEDIN_EMAIL, LINKEDIN_PASSWORD

COOKIES_FILE = "linkedin_cookies.json"

p = sync_playwright().start()  # ✅ Start Playwright manually


def login_to_linkedin():
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    print("🔍 Opening LinkedIn Login Page...")
    page.goto("https://www.linkedin.com/login")

    # Fill in login details
    page.fill("#username", LINKEDIN_EMAIL)
    page.fill("#password", LINKEDIN_PASSWORD)

    # Click login button
    page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")

    # ✅ Save cookies after logging in
    cookies = page.context.cookies()
    with open(COOKIES_FILE, "w") as f:
        json.dump(cookies, f)

    print("✅ Login successful! Cookies saved.")

    return page, browser  # ✅ Keep the browser open


if __name__ == "__main__":
    page, browser = login_to_linkedin()
    page.pause()  # ✅ Keeps the browser open for debugging
