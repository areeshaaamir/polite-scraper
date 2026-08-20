import requests
from pathlib import Path


URL = "https://books.toscrape.com/"

CACHE_DIR = Path("cache")
CACHE_FILE = CACHE_DIR / "catalogue-page-1.html"

HEADERS = {
    "User-Agent": "FlyRankInternship-A9/1.0"
}

TIMEOUT = 10


def fetch_page():
    if CACHE_FILE.exists():
        html = CACHE_FILE.read_text(encoding="utf-8")

        print("CACHE HIT")
        print(f"response_size={len(html)}")

        return html
    
    print("FETCH")

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=TIMEOUT
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"Failed to fetch page. Status code: {response.status_code}"
        )

    html = response.text

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    CACHE_FILE.write_text(
        html,
        encoding="utf-8"
    )

    print(f"response_size={len(html)}")

    return html


if __name__ == "__main__":
    fetch_page()