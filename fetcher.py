"""Fethcer for the bloodborne wiki"""

import time
import requests
from bs4 import BeautifulSoup

from config import USER_AGENT, REQUEST_DELAY_SECONDS

_session = requests.Session()
_session.headers.update({"User-Agent": USER_AGENT})


def fetch_html(url: str) -> str:
    """Fetching a single page"""
    r = _session.get(url, timeout=30)
    r.raise_for_status()
    return r.text


def fetch_all(urls: list[str]) -> dict[str, str]:
    """Fetch HTML for a list of URLs, with a polite delay between requests."""
    pages = {}
    for url in urls:
        print(f"Fetching {url}...")
        try:
            pages[url] = fetch_html(url)
        except requests.RequestException as e:
            print(f"  [error] {url}: {e}")
        time.sleep(REQUEST_DELAY_SECONDS)
    return pages
