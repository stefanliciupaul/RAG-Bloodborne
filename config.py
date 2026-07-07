"""config file for the Bloodborne Wiki scraper."""

BASE_URL = "https://www.bloodborne-wiki.com"

# the list of page URLs to scrape.
PAGE_URLS = [
    "https://www.bloodborne-wiki.com/2015/03/blood-starved-beast.html",
]

# hub page to auto-discover content links from 
INDEX_URL = None

OUTPUT_PATH = "wiki_chunks.jsonl"

MAX_CHUNK_SIZE = 1000

REQUEST_DELAY_SECONDS = 0.5  

USER_AGENT = "Mozilla/5.0 (compatible; BloodborneRAGBot/1.0; personal research project)"
