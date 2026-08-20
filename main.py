import requests
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time

URL = "https://books.toscrape.com/"

CACHE_DIR = Path("cache")

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0"
}

TIMEOUT = 10


def fetch_page(page_url, cache_file):
    if cache_file.exists():
        html = cache_file.read_text(encoding="utf-8")

        print(f"CACHE HIT:", {page_url})
        print(f"response_size={len(html)}")

        return html
    
    print(f"FETCH: ", {page_url})

    response = requests.get(
        page_url,
        headers=HEADERS,
        timeout=TIMEOUT
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to fetch page. Status code: {response.status_code}"
        )

    html = response.text

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    cache_file.write_text(
        html,
        encoding="utf-8"
    )

    return html

def get_books(html, page_url):
    
    soup = BeautifulSoup(html, "html.parser")
    
    links = []
    
    for article in soup.select("article.product_pod"):
        
        link = article.find("a")
        
        if link and link.get("href"):
            href = link["href"]
            absolute_url = urljoin(page_url, href)
            links.append(absolute_url)
            
    return links

def get_next_page(html, page_url):
    
    soup = BeautifulSoup(html, "html.parser")
    
    next_link = soup.select_one("li.next a")
    
    if next_link and next_link.get("href"):
        href = next_link["href"]
        
        return urljoin(page_url, href)
    
    return None

def discover_books():
    all_urls = []
    
    current = URL
    page = 1
    
    while page <= 3:
        cache_file = CACHE_DIR / f"catalogue-page-{page}.html"
        
        html = fetch_page(
            current,
            cache_file
        )
        
        book_urls = get_books(
            html,
            current
        )
        
        all_urls.extend(book_urls)
        
        print(
            f"page {page}: "
            f"found {len(book_urls)} books"
        )
        
        if page == 3:
            break
        
        next_url = get_next_page(
            html,
            current
        )
        
        if next_url is None:
            break

        current = next_url
        page += 1

        time.sleep(0.5)

    unique_urls = list(dict.fromkeys(all_urls))

    print()
    print(f"catalogue_pages={page}")
    print(f"discovered={len(all_urls)}")
    print(f"unique_urls={len(unique_urls)}")

    return unique_urls
    
if __name__ == "__main__":
    discover_books()