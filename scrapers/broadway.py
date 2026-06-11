"""Broadway musicals scraper — source: broadway-show-tickets.com (Headout-powered).

The listing page ships all shows in __NEXT_DATA__ at
props.pageProps.simplifiedCategoryTourListData.tourGroupMap (title, open/close
dates, availability, slug) — but NOT the venue. The venue name + exact
coordinates live on each show's detail page under
props.pageProps.tourGroupData.startLocation, so we fetch each detail page.
No external geocoding needed: coordinates are provided by the source.

Output: data/broadway.json   Run: python scrapers/broadway.py
"""

import json
import re
import sys
import io
import time
import urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DATA = Path(__file__).resolve().parent.parent / "data"
LISTING_URL = "https://www.broadway-show-tickets.com/musicals/"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MusicalMap/0.1"


BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Referer": "https://www.broadway-show-tickets.com/musicals/",
}


def fetch_html(url):
    req = urllib.request.Request(url, headers=BROWSER_HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def next_data(html):
    m = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.S
    )
    if not m:
        raise RuntimeError("No __NEXT_DATA__ — page structure changed")
    return json.loads(m.group(1))


def clean_date(v):
    if v is None:
        return None
    v = str(v).strip()
    return None if v.lower() in ("", "null", "none") else v


def detail_url(show_page_uid):
    """showPageUid 'www.broadway-show-tickets.com.<section>.<slug>' -> detail URL.

    Section is NOT always 'musicals' — some shows live under '/plays/'
    (e.g. Masquerade), so read the section straight from the uid.
    """
    parts = show_page_uid.split(".")
    if len(parts) >= 5:  # www . broadway-show-tickets . com . <section> . <slug>
        section, slug = parts[3], parts[4]
        return f"https://www.broadway-show-tickets.com/{section}/{slug}/"
    return None


def clean_text(v):
    """Strip whitespace incl. non-breaking spaces the source sometimes injects."""
    if not v:
        return None
    return v.replace("\xa0", " ").strip() or None


# All these shows are in NYC. The source occasionally returns swapped lat/lng or
# links the wrong same-named venue (e.g. Palace Theatre Manchester). Validate
# against an NYC bounding box: swap if that fixes it, else drop coords (a missing
# marker is better than a wrong one).
NYC_BBOX = (40.4, 41.0, -74.3, -73.6)  # lat_min, lat_max, lng_min, lng_max


def fix_nyc(lat, lng):
    if lat is None or lng is None:
        return None, None, "missing"

    def inbox(la, lo):
        return NYC_BBOX[0] <= la <= NYC_BBOX[1] and NYC_BBOX[2] <= lo <= NYC_BBOX[3]

    if inbox(lat, lng):
        return lat, lng, "ok"
    if inbox(lng, lat):
        return lng, lat, "swapped"
    return None, None, "out_of_region"


def parse_detail(html):
    """Return (venue, lat, lng, city) from a detail page, or (None,)*4."""
    data = next_data(html)
    loc = (data.get("props", {}).get("pageProps", {}).get("tourGroupData", {}) or {}).get(
        "startLocation"
    ) or {}
    venue = clean_text(loc.get("addressLine1"))
    city = clean_text(loc.get("cityName"))
    lat = loc.get("latitude")
    lng = loc.get("longitude")
    lat = round(float(lat), 6) if isinstance(lat, (int, float)) else None
    lng = round(float(lng), 6) if isinstance(lng, (int, float)) else None
    return venue, lat, lng, city


def main():
    print("Fetching Broadway listing…")
    listing = next_data(fetch_html(LISTING_URL))
    tgm = (
        listing["props"]["pageProps"]["simplifiedCategoryTourListData"]["tourGroupMap"]
    )
    print(f"Found {len(tgm)} shows. Fetching detail pages for venue + coords…")

    shows, no_venue = [], []
    for tgid, s in tgm.items():
        title = clean_text(s.get("title"))
        if not title or not s.get("available", True):
            continue
        url = detail_url(s.get("showPageUid", ""))
        venue = lat = lng = None
        city = "New York"
        if url:
            try:
                venue, lat, lng, dcity = parse_detail(fetch_html(url))
                city = dcity or city
            except Exception as e:  # noqa: BLE001
                print(f"  [detail] {title}: {e}")
            time.sleep(0.5)  # be polite

        lat, lng, geo_status = fix_nyc(lat, lng)
        if geo_status == "swapped":
            print(f"  [fix] {title}: swapped lat/lng")
        elif geo_status == "out_of_region":
            print(f"  [drop] {title}: coords outside NYC — dropped (likely wrong venue match)")

        rec = {
            "id": f"bway-{tgid}",
            "title": title,
            "type": "resident",
            "venue": venue or "(venue unknown)",
            "city": city,
            "country": "USA",
            "lat": lat,
            "lng": lng,
            "start_date": clean_date(s.get("reopeningDate")),
            "end_date": clean_date(s.get("closingDate")),
            "ticket_url": url or LISTING_URL,
            "image": None,
            "tour_name": None,
            "verified": True,
            "source": "broadway-show-tickets.com",
        }
        shows.append(rec)
        if lat is None:
            no_venue.append(title)
        print(f"  {title}  @ {rec['venue']}  ({lat},{lng})")

    out = {
        "meta": {
            "source": "broadway-show-tickets.com",
            "count": len(shows),
            "missing_coords": no_venue,
        },
        "shows": shows,
    }
    (DATA / "broadway.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"\nWrote {len(shows)} shows -> data/broadway.json")
    if no_venue:
        print(f"⚠ {len(no_venue)} without coords: {no_venue}")


if __name__ == "__main__":
    main()
