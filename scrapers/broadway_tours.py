"""North American touring musicals — aggregator scraper.
Source: broadway.org/tours (The Broadway League's official "Touring Broadway").

One scraper covers EVERY currently-touring show: the directory lists ~28 shows,
and each /tours/<slug> page lists its stops (city / venue / date range) under
"Currently Playing At" + "Upcoming Cities". Years aren't in the markup, so we
infer them: stops are chronological, so we start at the current year and roll
forward whenever a month goes backwards.

Each stop becomes a tour record (title groups with the resident production via
build_shows.py; poster is inherited there too). Only stops still running or
upcoming are kept. Output: data/tours.json   Run: python scrapers/broadway_tours.py
"""

import json
import re
import sys
import io
import time
import datetime
import urllib.request
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
sys.path.insert(0, str(Path(__file__).resolve().parent))
from geocode import geocode  # noqa: E402

DATA = Path(__file__).resolve().parent.parent / "data"
BASE = "https://www.broadway.org"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MusicalMap/0.1"
TODAY = datetime.date.today()
MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}

ROW_RE = re.compile(
    r'tour-date-loop[^>]*>\s*<div class="col col1">\s*'
    r'<div class="l1">([^<]+)</div>\s*'
    r'<div class="l2[^"]*">\s*(?:<a[^>]*>\s*([^<]+?)\s*</a>)?.*?'
    r'<div class="col col2">\s*<div class="l1">\s*([^<]+?)\s*</div>',
    re.S,
)


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8")


def tour_slugs(html):
    return sorted(set(re.findall(r'/tours/([a-z0-9-]+)', html)))


def show_title(html):
    m = re.search(r"<title>(.*?)</title>", html, re.S)
    raw = (m.group(1) if m else "").strip()
    return re.split(r"\s*[-|]\s*On Tour", raw)[0].strip() or raw


def show_image(html):
    # The real square key-art lives at /assets/shows/<slug>-...jpg.
    # (og:image is broadway.org's generic branding card — do NOT use it.)
    m = re.search(r'https?://[^"\']+/assets/shows/[^"\']+\.(?:jpg|jpeg|png|webp)', html)
    return m.group(0) if m else None


def parse_stops(html):
    """Yield dicts with city, venue, start_date, end_date (chronological year inference)."""
    cur_year, prev_month = TODAY.year, None
    for city, venue, drange in ROW_RE.findall(html):
        m = re.match(r"([A-Za-z]+)\s+(\d+)\s*[-–]\s*([A-Za-z]+)\s+(\d+)", drange.strip())
        if not m:  # single-day or odd format — skip
            continue
        sm, sd, em, ed = m.groups()
        smn, emn = MONTHS.get(sm[:3]), MONTHS.get(em[:3])
        if not smn or not emn:
            continue
        if prev_month and smn < prev_month:
            cur_year += 1
        prev_month = smn
        end_year = cur_year + 1 if emn < smn else cur_year
        start = datetime.date(cur_year, smn, int(sd))
        end = datetime.date(end_year, emn, int(ed))
        if end < TODAY:  # already finished
            continue
        yield {
            "city": city.strip(),
            "venue": (venue or city).strip(),
            "start_date": start.isoformat(),
            "end_date": end.isoformat(),
        }


def main():
    print("Fetching tours directory…")
    slugs = tour_slugs(fetch(BASE + "/tours"))
    print(f"{len(slugs)} touring shows listed.")

    shows = []
    for slug in slugs:
        try:
            html = fetch(f"{BASE}/tours/{slug}")
        except Exception as e:  # noqa: BLE001
            print(f"  [skip] {slug}: {e}")
            continue
        title = show_title(html)
        image = show_image(html)
        stops = list(parse_stops(html))
        print(f"  {title}  ({len(stops)} current/upcoming stops)")
        for st in stops:
            city = st["city"]
            # 巡演偶有國際站:Mexico City 曾被硬編碼成 USA(2026-07-09 座標交叉驗證抓到)
            country = ("Canada" if re.search(r",\s*(QC|ON|BC|AB|MB|SK|NS|NB|NL|PE)$", city)
                       else "Mexico" if re.match(r"(?i)mexico city|monterrey|guadalajara", city.strip())
                       else "USA")
            lat, lng = geocode(f"{st['venue']}|{city}".lower(),
                               f"{st['venue']}, {city}, {country}")
            if lat is None:  # fall back to city centroid
                lat, lng = geocode(f"city|{city}|{country}".lower(), f"{city}, {country}")
            sid = re.sub(r"[^a-z0-9]+", "-", f"{slug}-{st['city']}-{st['start_date']}".lower()).strip("-")
            shows.append({
                "id": f"tour-{sid}",
                "title": title,
                "type": "tour",
                "venue": st["venue"],
                "city": st["city"],
                "country": country,
                "lat": lat,
                "lng": lng,
                "start_date": st["start_date"],
                "end_date": st["end_date"],
                "ticket_url": f"{BASE}/tours/{slug}",
                "image": image,  # show poster from broadway.org (og:image)
                "tour_name": f"{title} — North American Tour",
                "verified": True,
                "source": "broadway.org",
            })
        time.sleep(0.4)

    out = {"meta": {"source": "broadway.org", "shows_count": len(slugs), "stops": len(shows)},
           "shows": shows}
    (DATA / "tours.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {len(shows)} tour stops ({len(slugs)} shows) -> data/tours.json")


if __name__ == "__main__":
    main()
