"""Venue geocoding with a persistent cache.

West End / Broadway theatres are a small, stable set, so we geocode each venue
once via OpenStreetMap Nominatim and cache the result forever in
data/venues.json keyed by a stable slug. Subsequent runs hit the cache and make
zero network calls. This keeps us off unreliable per-run geocoding and respects
Nominatim's usage policy (<=1 req/sec, descriptive User-Agent).
"""

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"
CACHE_FILE = DATA / "venues.json"
USER_AGENT = "MusicalMap/0.1 (https://github.com/dannynycc; dannynycc@gmail.com)"


def _load_cache():
    if CACHE_FILE.exists():
        return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
    return {}


def _save_cache(cache):
    CACHE_FILE.write_text(
        json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def geocode(slug, query):
    """Return (lat, lng) for a venue, using cache first then Nominatim.

    slug:  stable cache key (e.g. "his-majestys-theatre|London")
    query: human query for Nominatim (e.g. "His Majesty's Theatre, London, UK")
    Returns (None, None) and caches the miss-free None if not found.
    """
    cache = _load_cache()
    if slug in cache:
        c = cache[slug]
        return c.get("lat"), c.get("lng")

    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": query, "format": "json", "limit": 1}
    )
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    lat = lng = None
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            results = json.loads(r.read().decode("utf-8"))
        if results:
            lat = round(float(results[0]["lat"]), 6)
            lng = round(float(results[0]["lon"]), 6)
    except Exception as e:  # noqa: BLE001 — log and continue; a miss is non-fatal
        print(f"  [geocode] FAILED {query!r}: {e}")

    cache[slug] = {"lat": lat, "lng": lng, "query": query}
    _save_cache(cache)
    time.sleep(1.1)  # Nominatim rate limit: max 1 request/second
    return lat, lng
