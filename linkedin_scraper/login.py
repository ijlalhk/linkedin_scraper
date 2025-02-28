from playwright.sync_api import sync_playwright
import json
from linkedin_scraper.config import LINKEDIN_EMAIL, LINKEDIN_PASSWORD

COOKIES_FILE = "linkedin_cookies.json"


def login_to_linkedin(page, browser):
    print("🔍 Checking LinkedIn login status...")

    page.goto("https://www.linkedin.com/login", timeout=60000)  # Increase timeout to 60s

    # Ensure login page is fully loaded
    page.wait_for_load_state("domcontentloaded")

    # If already logged in, return
    if "feed" in page.url:
        print("✅ Already logged in.")
        return page, browser

    print("🔴 Not logged in. Attempting login...")

    # Fill in login details
    page.fill("#username", LINKEDIN_EMAIL)
    page.fill("#password", LINKEDIN_PASSWORD)

    # Click login button
    page.click("button[type=submit]")

    # Instead of waiting for networkidle, check for successful login
    page.wait_for_load_state("domcontentloaded")  # Ensure the login form loads
    page.wait_for_selector("div.global-nav", timeout=30000)  # Look for a known element after login

    # Verify successful login
    if "feed" in page.url:
        print("✅ Login successful!")
        # ✅ Save cookies after logging in
        cookies = page.context.cookies()
        with open(COOKIES_FILE, "w") as f:
            json.dump(cookies, f)
    else:
        print("❌ Login may have failed. Check manually.")

    return page, browser


if __name__ == '__main__':
    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            headless=False
        )
        page = browser.pages[0] if browser.pages else browser.new_page()

        page, browser = login_to_linkedin(page, browser)

        browser.close()
