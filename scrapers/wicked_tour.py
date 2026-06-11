"""Wicked — North American Tour scraper. Source: tour.wickedthemusical.com

Demonstrates the tour pattern: a touring production is many records (one per
city stop), each with a [start_date, end_date] run. The "current city" is
whichever stop contains today. Image is left null and inherited from the
resident Wicked poster by build_shows.py (a tour reuses the show's artwork).

Output: data/wicked_tour.json   Run: python scrapers/wicked_tour.py
"""

import json
import re
import sys
import io
import urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from geocode import geocode  # noqa: E402

DATA = Path(__file__).resolve().parent.parent / "data"
URL = "https://tour.wickedthemusical.com/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MusicalMap/0.1"
MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}

ROW_RE = re.compile(
    r'tour-city-listing__city">\s*<p[^>]*>([^<]+)</p>'
    r'.*?tour-city-listing__dates">\s*<p>\s*<strong>\s*([^<]+?)\s*</strong>'
    r'(?:.*?tour-city-listing__venue"><a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>)?',
    re.S,
)


def parse_range(s):
    """'May 6 - Jun 14 2026' / 'Dec 9 - Jan 3 2027' -> (start_iso, end_iso).
    Year is stated once at the end; start rolls back a year if it wraps."""
    m = re.match(r"([A-Za-z]+)\s+(\d+)\s*[-–]\s*([A-Za-z]+)\s+(\d+)\s+(\d{4})", s)
    if not m:
        return None, None
    sm, sd, em, ed, yr = m.groups()
    yr = int(yr)
    smn, emn = MONTHS.get(sm[:3]), MONTHS.get(em[:3])
    if not smn or not emn:
        return None, None
    start_year = yr if smn <= emn else yr - 1
    return f"{start_year}-{smn:02d}-{int(sd):02d}", f"{yr}-{emn:02d}-{int(ed):02d}"


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": UA})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    rows = ROW_RE.findall(html)
    print(f"Found {len(rows)} tour stops. Geocoding…")

    shows = []
    for city, drange, href, venue in rows:
        city = city.strip()
        venue = (venue or "").strip() or city
        start, end = parse_range(drange.strip())
        lat, lng = geocode(f"{venue}|{city}".lower(), f"{venue}, {city}, USA")
        slug = re.sub(r"[^a-z0-9]+", "-", f"{city}-{start}".lower()).strip("-")
        shows.append({
            "id": f"wicked-tour-{slug}",
            "title": "Wicked",
            "type": "tour",
            "venue": venue,
            "city": city,
            "country": "USA",
            "lat": lat,
            "lng": lng,
            "start_date": start,
            "end_date": end,
            "ticket_url": href or URL,
            "image": None,  # inherited from resident Wicked poster in build_shows.py
            "tour_name": "Wicked — North American Tour",
            "verified": True,
            "source": "tour.wickedthemusical.com",
        })
        print(f"  {city:18s} {start} – {end}  @ {venue}  ({lat},{lng})")

    out = {"meta": {"source": "tour.wickedthemusical.com", "count": len(shows)}, "shows": shows}
    (DATA / "wicked_tour.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {len(shows)} stops -> data/wicked_tour.json")


if __name__ == "__main__":
    main()
