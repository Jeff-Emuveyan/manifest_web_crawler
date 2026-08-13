from playwright.sync_api import sync_playwright
from urllib.parse import urlparse


def clean_url(url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def crawl_page(browser, page_number):
    url = f"https://themanifest.com/nl/software-development/companies?page={page_number}"

    page = browser.new_page()
    page.goto(url, wait_until="networkidle")

    buttons = page.get_by_text("Visit Site")

    websites = set()

    for i in range(buttons.count()):
        button = buttons.nth(i)

        redirect_url = button.get_attribute("href")

        if not redirect_url:
            continue

        company_page = browser.new_page()

        try:
            company_page.goto(
                redirect_url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            company_page.wait_for_timeout(3000)

            websites.add(clean_url(company_page.url))

        except Exception:
            pass

        finally:
            company_page.close()

    page.close()

    return sorted(websites)


def main():
    start_page = int(input("Enter start page: ").strip())
    end_page = int(input("Enter end page: ").strip())

    if start_page > end_page:
        print("Start page cannot be greater than end page.")
        return

    page_results = {}
    page_counts = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        for page_number in range(start_page, end_page + 1):
            websites = crawl_page(browser, page_number)
            page_results[page_number] = websites
            page_counts[page_number] = len(websites)

        browser.close()

    # Print all website URLs after crawling has completed
    for page_number in range(start_page, end_page + 1):
        for website in page_results[page_number]:
            print(website)

        # Three blank lines
        print("\n\n\n", end="")

    # Summary report
    print("========== Crawl Report ==========")
    print(f"Start Page : {start_page}")
    print(f"End Page   : {end_page}")
    print()

    for page_number in range(start_page, end_page + 1):
        print(f"Page {page_number}: {page_counts[page_number]} website(s)")

    print()
    print(f"Total Pages Crawled: {end_page - start_page + 1}")


if __name__ == "__main__":
    main()