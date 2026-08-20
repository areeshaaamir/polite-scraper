import requests
import time
from pathlib import Path
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import datetime, timezone


BASE_URL = "https://books.toscrape.com/"

CACHE_DIR = Path("cache")

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0"
}

TIMEOUT = 10

def get_page(page_url, cache_file):

    if cache_file.exists():

        html = cache_file.read_text(
            encoding="utf-8"
        )

        print(f"CACHE HIT: {page_url}")

        return html

    print(f"FETCH: {page_url}")

    response = requests.get(
        page_url,
        headers=HEADERS,
        timeout=TIMEOUT
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to fetch {page_url}: "
            f"{response.status_code}"
        )

    html = response.text

    CACHE_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    cache_file.write_text(
        html,
        encoding="utf-8"
    )

    return html

def find_books(html, page_url):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    book_links = []

    for article in soup.select(
        "article.product_pod"
    ):

        link = article.find("a")

        if link and link.get("href"):

            href = link["href"]

            absolute_url = urljoin(
                page_url,
                href
            )

            book_links.append(
                absolute_url
            )

    return book_links

def find_next_page(html, page_url):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    next_link = soup.select_one(
        "li.next a"
    )

    if next_link and next_link.get("href"):

        href = next_link["href"]

        return urljoin(
            page_url,
            href
        )

    return None

def discover_books():

    all_book_urls = []

    book_sources = []

    current_url = BASE_URL

    page_number = 1

    while page_number <= 3:

        cache_file = (
            CACHE_DIR
            / f"catalogue-page-{page_number}.html"
        )

        html = get_page(
            current_url,
            cache_file
        )

        book_urls = find_books(
            html,
            current_url
        )

        for book_url in book_urls:

            all_book_urls.append(book_url)

            book_sources.append({
                "product_url": book_url,
                "source_page": current_url
            })

        print(
            f"page {page_number}: "
            f"found {len(book_urls)} books"
        )

        if page_number == 3:
            break

        next_url = find_next_page(
            html,
            current_url
        )

        if next_url is None:
            break

        current_url = next_url

        page_number += 1

        time.sleep(0.5)

    unique_urls = list(
        dict.fromkeys(all_book_urls)
    )

    print()
    print(f"catalogue_pages={page_number}")
    print(f"discovered={len(all_book_urls)}")
    print(f"unique_urls={len(unique_urls)}")

    return book_sources

def extract_book(
    html,
    product_url,
    source_page
):

    soup = BeautifulSoup(
        html,
        "html.parser"
    )

    title_element = soup.select_one(
        "div.product_main h1"
    )

    if title_element:
        title = title_element.get_text(
            strip=True
        )
    else:
        title = None

    price_element = soup.select_one(
        "div.product_main p.price_color"
    )

    if price_element:
        price_text = price_element.get_text(
            strip=True
        )
    else:
        price_text = None

    availability_element = soup.select_one(
        "div.product_main p.instock.availability"
    )

    if availability_element:
        availability_text = (
            availability_element.get_text(
                " ",
                strip=True
            )
        )
    else:
        availability_text = None

    rating_element = soup.select_one(
        "div.product_main p.star-rating"
    )

    if rating_element:

        classes = rating_element.get(
            "class",
            []
        )

        rating_text = next(
            (
                class_name
                for class_name in classes
                if class_name != "star-rating"
            ),
            None
        )

    else:
        rating_text = None

    description_element = soup.select_one(
        "#product_description + p"
    )

    if description_element:

        description = (
            description_element.get_text(
                " ",
                strip=True
            )
        )

    else:

        description = None

    fetched_at = datetime.now(
        timezone.utc
    ).isoformat()

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": fetched_at
    }

def extract_all_books(book_sources):

    records = []

    for number, book in enumerate(
        book_sources,
        start=1
    ):

        product_url = book["product_url"]

        source_page = book["source_page"]

        print()
        print(
            f"Processing book "
            f"{number}/{len(book_sources)}"
        )

        cache_file = (
            CACHE_DIR
            / f"book-{number}.html"
        )

        html = get_page(
            product_url,
            cache_file
        )

        record = extract_book(
            html,
            product_url,
            source_page
        )

        records.append(record)

        if not cache_file.exists():
            time.sleep(0.5)

    return records

if __name__ == "__main__":

    book_sources = discover_books()

    print()

    records = extract_all_books(
        book_sources
    )

    print()

    print(
        f"detail_pages={len(records)}"
    )

    print()

    print("ONE RAW RECORD:")
    print(records[0])