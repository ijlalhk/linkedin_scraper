import pandas as pd
from playwright.sync_api import sync_playwright

books_data = []


def scrape_books():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # Keep browser open for debugging
        page = browser.new_page()

        print("🔍 Opening Books to Scrape website...")
        page.goto("http://books.toscrape.com/")

        # Wait for the page to load
        page.wait_for_load_state("load")

        # Get all book titles
        all_books = page.locator("article.product_pod").all()
        print(f"✅ Found {len(all_books)} books!")

        for book in all_books:
            # Extract Title (from the 'title' attribute inside <a>)
            title = book.locator("h3 a").get_attribute("title")

            # Extract Book Link (from the 'href' attribute inside <a>)
            book_link = book.locator("h3 a").get_attribute("href")
            full_link = f"http://books.toscrape.com/{book_link}"  # Complete the URL

            # Extract Price (text content of <p class="price_color">)
            price = book.locator(".price_color").text_content().strip()

            # Extract Stock Status (text content of <p class="instock availability">)
            stock = book.locator(".instock.availability").text_content().strip()

            # Extract Rating (from the 'class' attribute of <p class="star-rating One">)
            rating_class = book.locator(".star-rating").get_attribute("class")  # Example: "star-rating One"
            rating = rating_class.split()[-1]  # Extract "One", "Two", etc.

            # Store data in dictionary
            book_info = {
                "Title": title,
                "Price": price,
                "Stock": stock,
                "Rating": rating,
                "Link": full_link
            }
            books_data.append(book_info)  # Add dictionary to list

        browser.close()
        print(books_data[:3])
        return books_data


if __name__ == "__main__":
    books_data = scrape_books()
    # Convert to DataFrame
    df = pd.DataFrame(books_data)

    # Save to Excel
    df.to_excel("books.xlsx", index=False)
    print(f"📚 Scraped {len(books_data)} books!")
