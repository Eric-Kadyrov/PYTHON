import requests
from bs4 import BeautifulSoup

def scrape_links(url):
    try:
        # Send HTTP request
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.text, "html.parser")

        print(f"\nScraping: {url}\n")
        print("Links found:\n")

        # Find all <a> tags
        links = soup.find_all("a")

        for i, link in enumerate(links, start=1):
            text = link.get_text(strip=True)
            href = link.get("href")

            if href:  # only print links with href
                print(f"{i}. Text: {text if text else '[No text]'}")
                print(f"   URL: {href}\n")

    except requests.exceptions.RequestException as e:
        print("Error while fetching the page:")
        print(e)


# Prompt user for website
website = input("Enter website URL (example: https://example.com): ").strip()

scrape_links(website)