from playwright.sync_api import sync_playwright
from urllib.parse import urlparse

def clean_url(url):
    parsed = urlparse(url)
    return f"{parsed.scheme}://{parsed.netloc}"

def main():
    page_number = input("Enter page number: ").strip()

    url = f"https://themanifest.com/nl/software-development/companies?page={page_number}"

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)

        page = browser.new_page()

        print("Loading page...")
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

        print("\n==============================")
        print("Company Websites")
        print("==============================\n")

        for index, website in enumerate(sorted(websites), start=1):
            print(f"{index}. {website}")

        print(f"\nFound {len(websites)} unique websites.")

        browser.close()

if __name__ == "__main__":
    main()