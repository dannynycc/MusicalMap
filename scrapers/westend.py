"""West End musicals scraper — source: londontheatre.co.uk

Strategy: the listing page is a Next.js app that ships all show data in the
embedded __NEXT_DATA__ JSON blob. We parse that (far more stable than scraping
DOM classes) and geocode each venue via scrapers/geocode.py.

Output: data/westend.json (a normalized source file; build_shows.py merges all
source files into data/shows.json).

Run:  python scrapers/westend.py
"""

import json
import re
import sys
import io
import urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")  # Windows: force UTF-8 stdout

sys.path.insert(0, str(Path(__file__).resolve().parent))  # run from any cwd
from geocode import geocode  # noqa: E402

DATA = Path(__file__).resolve().parent.parent / "data"
LISTING_URL = "https://www.londontheatre.co.uk/whats-on/musicals?categories=Musicals"
SHOW_URL = "https://www.londontheatre.co.uk/show/{slug}"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MusicalMap/0.1"


def fetch_html(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def extract_products(html):
    """Return de-duplicated product dicts from __NEXT_DATA__."""
    m = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S
    )
    if not m:
        raise RuntimeError("No __NEXT_DATA__ found — page structure changed")
    data = json.loads(m.group(1))
    cat = data["props"]["pageProps"]["category"]
    products = {}
    for sub in cat.get("subcategories") or []:
        for p in (sub.get("productList") or {}).get("products") or []:
            slug = p.get("slug")
            if slug:
                products[slug] = p  # de-dup by slug
    return list(products.values())


# Non-show entries that slip into the musicals category (gift cards etc.)
SKIP_SLUGS = {"london-theatre-gift-cards"}


def clean_date(v):
    """Source sometimes uses the string 'null' / '' for empty dates."""
    if v is None:
        return None
    v = str(v).strip()
    return None if v.lower() in ("", "null", "none") else v


def normalize(p):
    slug = p.get("slug")
    if slug in SKIP_SLUGS:
        return None
    title = (p.get("name") or p.get("displayName") or "").strip()
    venue = p.get("venue") or {}
    venue_name = (venue.get("name") or "").strip()
    venue_slug = venue.get("url") or venue_name.lower().replace(" ", "-")
    if not title or not venue_name:
        return None

    lat, lng = geocode(
        f"{venue_slug}|London",
        f"{venue_name}, London, UK",
    )

    end = clean_date(p.get("bookingTo")) or clean_date(p.get("closingDate"))  # null = open-ended
    return {
        "id": f"westend-{slug}",
        "title": title,
        "type": "resident",
        "venue": venue_name,
        "city": "London",
        "country": "UK",
        "lat": lat,
        "lng": lng,
        "start_date": clean_date(p.get("startingDate")),
        "end_date": end,
        "ticket_url": SHOW_URL.format(slug=slug),
        "image": None,
        "tour_name": None,
        "verified": True,
        "source": "londontheatre.co.uk",
    }


def main():
    print("Fetching West End listing…")
    html = fetch_html(LISTING_URL)
    products = extract_products(html)
    print(f"Found {len(products)} products. Normalizing + geocoding…")

    shows, missing_coords = [], []
    for p in products:
        rec = normalize(p)
        if not rec:
            continue
        shows.append(rec)
        if rec["lat"] is None:
            missing_coords.append(rec["venue"])
        print(f"  {rec['title']}  @ {rec['venue']}  ({rec['lat']},{rec['lng']})")

    out = {
        "meta": {
            "source": "londontheatre.co.uk",
            "count": len(shows),
            "missing_coords": sorted(set(missing_coords)),
        },
        "shows": shows,
    }
    (DATA / "westend.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nWrote {len(shows)} shows -> data/westend.json")
    if missing_coords:
        print(f"⚠ {len(set(missing_coords))} venues missing coords: {sorted(set(missing_coords))}")


if __name__ == "__main__":
    main()
