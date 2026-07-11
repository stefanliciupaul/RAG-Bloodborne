"""config file for the Bloodborne Wiki scraper."""

BASE_URL = "https://www.bloodborne-wiki.com"

# hardcoded boss page URLs
PAGE_URLS = [
    # Main story bosses
    "https://www.bloodborne-wiki.com/2015/03/cleric-beast.html",
    "https://www.bloodborne-wiki.com/2015/03/father-gascoigne.html",
    "https://www.bloodborne-wiki.com/2015/03/blood-starved-beast.html",
    "https://www.bloodborne-wiki.com/2015/03/hemwick-witch.html",
    "https://www.bloodborne-wiki.com/2015/02/darkbeast-paarl.html",
    "https://www.bloodborne-wiki.com/2015/03/vicar-amelia.html",
    "https://www.bloodborne-wiki.com/2015/03/shadow-of-yharnam.html",
    "https://www.bloodborne-wiki.com/2015/03/martyr-logarius.html",
    "https://www.bloodborne-wiki.com/2015/03/amygdala.html",
    "https://www.bloodborne-wiki.com/2015/03/rom-vacuous-spider.html",
    "https://www.bloodborne-wiki.com/2015/03/the-one-reborn.html",
    "https://www.bloodborne-wiki.com/2015/03/celestial-emissary.html",
    "https://www.bloodborne-wiki.com/2015/03/ebrietas-daughter-of-cosmos.html",
    "https://www.bloodborne-wiki.com/2015/03/micolash-host-of-nightmare.html",
    "https://www.bloodborne-wiki.com/2015/03/mergos-wet-nurse.html",
    "https://www.bloodborne-wiki.com/2015/04/gehrman-first-hunter.html",
    "https://www.bloodborne-wiki.com/2015/03/moon-presence.html",
    # The Old Hunters DLC bosses
    "https://www.bloodborne-wiki.com/2015/10/ludwig.html",
    "https://www.bloodborne-wiki.com/2015/11/laurence-first-vicar.html",
    "https://www.bloodborne-wiki.com/2015/11/living-failures.html",
    "https://www.bloodborne-wiki.com/2015/11/lady-maria-of-astral-clocktower.html",
    "https://www.bloodborne-wiki.com/2015/11/orphan-of-kos.html",
    # Chalice dungeon bosses (not already included)
    "https://www.bloodborne-wiki.com/2015/03/undead-giant.html",
    "https://www.bloodborne-wiki.com/2015/10/merciless-watchers-watcher-chieftain.html",
    "https://www.bloodborne-wiki.com/2015/03/ancient-guard-dog.html",
    "https://www.bloodborne-wiki.com/2015/03/beast-possessed-soul.html",
    "https://www.bloodborne-wiki.com/2015/03/keeper-of-old-lords.html",
    "https://www.bloodborne-wiki.com/2015/03/pthumerian-descendant.html",
    "https://www.bloodborne-wiki.com/2015/07/undead-giant-club-and-hook.html",
    "https://www.bloodborne-wiki.com/2015/03/bloodletting-beast.html",
    "https://www.bloodborne-wiki.com/2015/04/yharnam-pthumerian-queen.html",
    "https://www.bloodborne-wiki.com/2015/03/maneater-boar.html",
    "https://www.bloodborne-wiki.com/2015/08/undead-giant-hatchet-and-cannon.html",
    "https://www.bloodborne-wiki.com/2015/04/brainsucker.html",
    "https://www.bloodborne-wiki.com/2015/04/forgotten-madman.html",
    "https://www.bloodborne-wiki.com/2015/03/pthumerian-elder.html",
    "https://www.bloodborne-wiki.com/2015/03/abhorrent-beast.html",
    "https://www.bloodborne-wiki.com/2015/06/loran-silverbeast.html",
]

# these are the sections of the website that are scraped
SECTION_ALLOWLIST = [
    "description",
    "preparation",
    "overview",
    "strategy",
    "attack pattern",
    "weak point",
    "environment",
]

OUTPUT_PATH = "wiki_chunks.jsonl"

# nr of pages the paragraph must appear under for it to be removed from the chunks
BOILERPLATE_MIN_PAGES = 3
BOILERPLATE_MIN_FRACTION = 0.5

MAX_CHUNK_CHARS = 2000

REQUEST_DELAY_SECONDS = 0.5

USER_AGENT = "Mozilla/5.0 (compatible; BloodborneRAGBot/1.0; personal research project)"
