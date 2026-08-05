from playwright.sync_api import sync_playwright
from urllib.parse import urlparse


def clean_url(url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"


def crawl_page(browser, page_number):
    url = f"https://themanifest.com/nl/software-development/companies?page={page_number}"

    page = browser.new_page()

    print(f"\nLoading page {page_number}...")
    page.goto(url, wait_until="networkidle")

    buttons = page.get_by_text("Visit Site")

    print(f"Found {buttons.count()} companies.\n")

    websites = set()

    for i in range(buttons.count()):
        button = buttons.nth(i)

        redirect_url = button.get_attribute("href")

        if not redirect_url:
            continue

        print(f"Checking company {i + 1}...")

        company_page = browser.new_page()

        try:
            company_page.goto(
                redirect_url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            # Wait a little for redirects to finish
            company_page.wait_for_timeout(3000)

            final_url = company_page.url
            websites.add(clean_url(final_url))

        except Exception as e:
            print(f"Failed: {e}")

        finally:
            company_page.close()

    page.close()

    print("\n==============================")
    print(f"Company Websites (Page {page_number})")
    print("==============================\n")

    for index, website in enumerate(sorted(websites), start=1):
        print(f"{index}. {website}")

    print(f"\nFound {len(websites)} unique websites on page {page_number}.")

    # Three blank lines for readability
    print("\n\n\n")


def main():
    start_page = int(input("Enter start page: ").strip())
    end_page = int(input("Enter end page: ").strip())

    if start_page > end_page:
        print("Start page cannot be greater than end page.")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)

        for page_number in range(start_page, end_page + 1):
            crawl_page(browser, page_number)

        browser.close()


if __name__ == "__main__":
    main()