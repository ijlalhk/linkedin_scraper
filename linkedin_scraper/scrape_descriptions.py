import random
import pandas as pd
import time
from playwright.sync_api import sync_playwright

profile_path = "C:/Users/Biome/AppData/Local/Google/Chrome/User Data/Default"  # Use existing profile


def get_job_description(page, job_link):
    """Extracts job description from the job posting page."""
    try:
        page.goto(job_link, timeout=30000)
        page.wait_for_load_state("domcontentloaded")
        time.sleep(random.uniform(2, 8))
        # Adjust the selector if needed
        # page.pause()
        page.get_by_role("button", name="Click to see more description").click()
        page.get_by_role("article").click()
        job_description = page.locator("div.jobs-description__content").text_content()

        return job_description.strip() if job_description else "Not available"
    except Exception as e:
        print(f"Error fetching job description for {job_link}: {e}")
        return "Error fetching"


def scrape_job_descriptions():
    """Loads saved jobs from Excel, scrapes descriptions, and updates file."""
    df = pd.read_excel("jobs.xlsx")

    if "description" in df.columns:
        print("Descriptions already exists for the job. Skipping previously scraped entries.")
        df["description"].fillna("", inplace=True)
    else:
        df["description"] = ""

    with sync_playwright() as p:
        browser = p.chromium.launch_persistent_context(
            user_data_dir=profile_path, headless=False
        )
        page = browser.pages[0] if browser.pages else browser.new_page()

        for index, row in df.iterrows():
            if row["description"]:  # Skip if description already exists
                print(f"Skipping {row['title']} (already scraped)")
                continue

            job_link = row["link"]
            if job_link and isinstance(job_link, str):
                print(f"Scraping description for: {row['title']}")
                df.at[index, "description"] = get_job_description(page, job_link)
                time.sleep(3)  # Sleep to avoid rate limits

        browser.close()

    df.to_excel("jobs_with_description.xlsx", index=False)
    print("✅ Job descriptions updated successfully!")


if __name__ == '__main__':
    scrape_job_descriptions()
