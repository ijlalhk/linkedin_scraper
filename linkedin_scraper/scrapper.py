"""Scrape jobs from LinkedIn"""
from linkedin_scraper.login import login_to_linkedin
from bs4 import BeautifulSoup
import pandas as pd

def scrape_jobs():
    page, browser = login_to_linkedin()

    print("Login successful")

    page.goto("https://www.linkedin.com/feed/")
    page.get_by_role("combobox", name="Search").click()
    page.get_by_text("python developer", exact=True).click()

    # Get all job listings
    # page.pause()
    # job_listings = page.locator("ul.vYQyzaFxCTwMqGPkxJcPDbkCcUoIqHbYees li")
    # print(f"Found {len(job_listings.all())} job listings")
    #
    job_listings = page.locator("li:has(div.job-card-container)")
    print(f"Found {job_listings.count()} job listings")

    all_job_html = "\n".join(job.inner_html() for job in job_listings.all())  # Convert to string

    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(all_job_html, "html.parser")

    # Find all job listings
    job_listings = soup.find_all("li", class_="scaffold-layout__list-item")

    # Extract job details
    jobs_data = []
    for job in job_listings:
        job_data = {}

        # Job Title
        title_element = job.find("a", class_="job-card-container__link")
        job_data["title"] = title_element.text.strip() if title_element else None

        # Company Name
        company_element = job.find("span", class_="YGkphPWJLcZoKjqmMHJWIZxpuIGCXJaMct")
        job_data["company"] = company_element.text.strip() if company_element else None

        # Job Location
        location_element = job.find("li", class_="zVOXfdhNOUpuINtMHxaECEfbEVlDkYhgavq")
        job_data["location"] = location_element.text.strip() if location_element else None

        # Job Link
        job_data["link"] = "https://www.linkedin.com" + title_element["href"] if title_element else None

        # Append to list
        jobs_data.append(job_data)

    return jobs_data

if __name__ == "__main__":
    jobsdata = scrape_jobs()

    if jobsdata:
        df = pd.DataFrame(jobsdata)
        df.to_excel("jobs.xlsx", index=False)
        print(f"✅ Scraped {len(jobsdata)} jobs!")
    else:
        print("❌ No jobs found.")
