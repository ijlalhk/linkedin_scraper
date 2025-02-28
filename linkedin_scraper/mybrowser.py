import pandas as pd
from playwright.sync_api import sync_playwright
import random
import time
from login import login_to_linkedin

profile_path = "C:/Users/Biome/AppData/Local/Google/Chrome/User Data/Default"  # Use the detected profile
job_title = "data analyst"  # Job title to search for
page = None


def smooth_scroll_until_bottom(page):
    job_list_parent = page.locator("xpath=//*[@id='main']/div/div[2]/div[1]/div")

    print("📜 Starting smooth scrolling in job list container...")

    last_height = job_list_parent.evaluate("el => el.scrollHeight")  # Get initial height
    scroll_step = 300  # Pixels per scroll step
    delay = 0.5  # Pause for jobs to load
    max_attempts = 20  # Prevent infinite loops
    stable_attempts = 0  # Count of stable heights before stopping
    stable_threshold = 3  # Stop after 3 consecutive stable heights

    for attempt in range(max_attempts):
        print(f"📜 Scrolling attempt {attempt + 1}...")

        # Scroll down smoothly
        job_list_parent.evaluate("(el, step) => el.scrollBy(0, step)", scroll_step)
        time.sleep(delay)  # Allow jobs to load

        new_height = job_list_parent.evaluate("el => el.scrollHeight")  # Get updated height

        if new_height == last_height:
            stable_attempts += 1
            print(f"🟡 No new jobs detected ({stable_attempts}/{stable_threshold})")
            if stable_attempts >= stable_threshold:
                print("✅ No more new jobs detected. Stopping scrolling.")
                break  # Stop after stable attempts
        else:
            stable_attempts = 0  # Reset if height changes

        last_height = new_height  # Update last known height

    print("📜 Finished smooth scrolling.")


def scrape_linkedin_jobs():
    max_pages = 2
    current_page = 1

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_path,
            headless=False
        )
        page = browser.pages[0] if browser.pages else browser.new_page()

        # Pass page & browser to login method instead of creating a new one
        page, browser = login_to_linkedin(page, browser)

        print("✅ Successfully logged in!")

        search_box = page.get_by_role("combobox", name="Search")
        search_box.click()
        search_box.fill(job_title)
        search_box.press("Enter")
        page.get_by_text("See all job results in", exact=False).nth(0).click()
        page.wait_for_load_state("domcontentloaded")

        jobs_data = []

        while current_page <= max_pages:
            time.sleep(random.uniform(2, 5))
            smooth_scroll_until_bottom(page)
            page.wait_for_selector("ul >> li[data-occludable-job-id]", timeout=10000)

            job_listings = page.locator("ul >> li[data-occludable-job-id]")
            print(f"Found {len(job_listings.all())} job listings")
            time.sleep(10)

            for job in job_listings.element_handles():
                try:
                    title_element = job.query_selector("a.job-card-container__link")
                    title = title_element.inner_text().strip() if title_element else None
                    job_link = f"https://www.linkedin.com{title_element.get_attribute('href')}" if title_element else None

                    company_element = job.query_selector("span.YGkphPWJLcZoKjqmMHJWIZxpuIGCXJaMct")
                    company = company_element.text_content().strip() if company_element else None

                    location_element = job.query_selector("li.zVOXfdhNOUpuINtMHxaECEfbEVlDkYhgavq")
                    location = location_element.text_content().strip() if location_element else None

                    current_job_data = {
                        "title": title,
                        "company": company,
                        "location": location,
                        "link": job_link
                    }
                    print(current_job_data)
                    jobs_data.append(current_job_data)

                except Exception as e:
                    print(f"Error: {e}")

            next_button = page.locator("button.jobs-search-pagination__button--next")
            if next_button.count() == 0 or not next_button.is_visible():
                print("No more pages to scrape. Stopping...")
                break

            print("Navigating to next page...")
            next_button.click()
            current_page += 1
            page.wait_for_load_state("domcontentloaded")

    return jobs_data


if __name__ == '__main__':

    j_data = scrape_linkedin_jobs()
    print(j_data)

    if j_data:
        df = pd.DataFrame(j_data)
        df.to_excel("jobs.xlsx", index=False)
        print(f"✅ Scraped {len(j_data)} jobs!")
    else:
        print("❌ No jobs found.")
