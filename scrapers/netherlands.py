"""Netherlands musicals — source: stage-entertainment.nl

Stage Entertainment runs the big sit-down musicals in NL. The site is the same
server-rendered platform as stage-entertainment.de (see stage_de.py), so a plain
static fetch with a browser UA is enough — no headless browser, no API.

How we collect:
  - The musicals overview (/musicals-nederland) and each venue agenda page list
    show links. The path segment IS the genre: /shows/musical/{slug} are MUSICALS,
    /shows/theater/{slug} are plays (e.g. Harry Potter) — we keep only musical/.
  - Each show page is read for: title (og:title, first segment before the "|"),
    venue (most-mentioned known Stage house in the page — the og:title second
    segment is unreliable, sometimes a marketing phrase like "Vanaf september"),
    city (from the venue), poster (og:image, else a show-matching mediaportal
    image) and the run end-date (Dutch body phrase "tot en met {day} {month}").

Dates: Stage NL runs are open-ended sit-down residencies. JSON-LD startDate is
the production premiere (years ago), not the current window, so we ignore it and
treat start_date as null (= playing now). end_date comes from the "tot en met"
closing-date phrase when the page advertises one, else null (open-ended).

Titles are kept AS SHOWN (Dutch or English) — the central build handles tagging.

Output: data/netherlands.json    Run: python scrapers/netherlands.py
"""

import html as htmllib
import io
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone, timedelta
from hashlib import md5
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

DATA = Path(__file__).resolve().parent.parent / "data"
BASE = "https://www.stage-entertainment.nl"
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MusicalMap/0.1"}
CET = timezone(timedelta(hours=2))  # NL summer time; only used for "today"
SOURCE = "stage-entertainment.nl"

# Pages that list show links. The per-venue pages surface shows playing in
# Scheveningen/Utrecht even when they are not featured on the main overview.
# (Beatrix has an /agenda sub-page; AFAS only has its base theater page.)
SEED_PAGES = [
    f"{BASE}/musicals-nederland",
    f"{BASE}/theaters/beatrix-theater-utrecht/agenda",
    f"{BASE}/theaters/beatrix-theater-utrecht",
    f"{BASE}/theaters/afas-circustheater-scheveningen",
]

# Slugs that match /shows/musical/ but are not actually shows.
NON_SHOW_SLUGS = {"nieuwsbrief-inschrijven", "boeknu"}

# Stage's NL houses (+ two Amsterdam houses that may appear), with building-level
# coords looked up from maps. Key = lowercase substring matched against page text.
VENUES = {
    "beatrix theater": ("Beatrix Theater Utrecht", "Utrecht", 52.0894, 5.1098),
    "afas circustheater": ("AFAS Circustheater", "Scheveningen", 52.1083, 4.2769),
    "circustheater": ("AFAS Circustheater", "Scheveningen", 52.1083, 4.2769),
    "delamar": ("DeLaMar Theater", "Amsterdam", 52.3628, 4.8797),
    "carré": ("Royal Theater Carré", "Amsterdam", 52.3625, 4.9043),
    "carre": ("Royal Theater Carré", "Amsterdam", 52.3625, 4.9043),
}

DUTCH_MONTHS = {
    "januari": 1, "februari": 2, "maart": 3, "april": 4, "mei": 5, "juni": 6,
    "juli": 7, "augustus": 8, "september": 9, "oktober": 10, "november": 11,
    "december": 12,
}


def fetch(url):
    req = urllib.request.Request(url, headers=UA)
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")


def collect_musical_slugs():
    """Return the set of /shows/musical/{slug} slugs across all seed pages."""
    slugs = set()
    for page in SEED_PAGES:
        try:
            html = fetch(page)
        except Exception as e:  # noqa: BLE001
            print(f"  [seed skip] {page}: {e}")
            continue
        for genre, slug in re.findall(r"/shows/(musical|theater)/([a-z0-9-]+)", html):
            if genre != "musical":      # genre filter: drop /shows/theater/ (plays)
                continue
            if slug in NON_SHOW_SLUGS:  # newsletter / "book now" sub-paths
                continue
            slugs.add(slug)
    return slugs


def parse_end_date(html, today):
    """Parse the Dutch closing-date phrase 'tot en met {day} {month}' -> ISO.

    The page omits the year, so pick the nearest future occurrence (this year if
    the date is still ahead, otherwise next year). Returns None if absent.
    """
    m = re.search(
        r"tot en met\s+(\d{1,2})\s+(" + "|".join(DUTCH_MONTHS) + r")", html, re.I
    )
    if not m:
        return None
    day, month = int(m.group(1)), DUTCH_MONTHS[m.group(2).lower()]
    year = today.year
    for y in (year, year + 1):
        cand = f"{y:04d}-{month:02d}-{day:02d}"
        if cand >= today.strftime("%Y-%m-%d"):
            return cand
    return None


def pick_venue(html):
    """Match the most-mentioned known venue substring -> (name, city, lat, lng)."""
    text = html.lower()
    counts = {k: text.count(k) for k in VENUES}
    best = max(counts, key=lambda k: counts[k])
    if counts[best] == 0:
        return None
    return VENUES[best]


def clean_img(url):
    """Decode HTML entities and drop the ?io=transform resize query so the
    poster is returned at full size rather than a 180px thumbnail."""
    return htmllib.unescape(url).split("?io=")[0]


def pick_image(html, slug):
    """Prefer og:image; else a mediaportal image whose filename matches the show."""
    og = re.search(r'property="og:image" content="([^"]+)"', html)
    if og:
        return clean_img(og.group(1))
    # Build a keyword from the slug (e.g. andjuliet -> "juliet") and match a
    # mediaportal asset filename, avoiding generic venue/logo images.
    key = slug.replace("and", "").replace("musical", "")
    for url in re.findall(r"(https://mediaportal\.stage-entertainment\.com/[^\"' )]+)", html):
        fname = url.rsplit("/", 1)[-1].lower()
        if key and key[:4] in fname and "logo" not in fname:
            return clean_img(url)
    return None


def main():
    slugs = sorted(collect_musical_slugs())
    print(f"{len(slugs)} musical show slugs: {slugs}")
    today = datetime.now(CET)
    today_str = today.strftime("%Y-%m-%d")

    kept, dropped = [], []
    for slug in slugs:
        url = f"{BASE}/shows/musical/{slug}"
        try:
            html = fetch(url)
        except Exception as e:  # noqa: BLE001
            dropped.append(f"{slug} (fetch error: {e})")
            continue

        tm = re.search(r'property="og:title" content="([^"]+)"', html) \
            or re.search(r"<title>([^<]+)</title>", html)
        if not tm:
            dropped.append(f"{slug} (no title)")
            continue
        title = htmllib.unescape(tm.group(1).split("|")[0]).strip()

        venue = pick_venue(html)
        if not venue:
            dropped.append(f"{title} (no known venue)")
            continue
        vname, city, lat, lng = venue

        end_date = parse_end_date(html, today)
        if end_date is not None and end_date < today_str:
            dropped.append(f"{title} (ended {end_date})")
            continue

        kept.append({
            "title": title, "venue": vname, "city": city,
            "lat": lat, "lng": lng, "end_date": end_date,
            "image": pick_image(html, slug), "url": url,
        })
        print(f"  keep: {title[:34]:36s} @ {vname[:26]:28s} {city:13s} end={end_date}")
        time.sleep(0.3)

    shows = []
    for s in kept:
        sid = "nl-" + md5(f"{SOURCE}|{s['title']}|{s['venue']}".encode()).hexdigest()[:8]
        shows.append({
            "id": sid, "title": s["title"], "title_en": "",
            "venue": s["venue"], "city": s["city"], "country": "Netherlands",
            "lat": s["lat"], "lng": s["lng"],
            "start_date": None, "end_date": s["end_date"],
            "image": s["image"], "ticket_url": s["url"],
            "type": "resident", "verified": True, "source": SOURCE,
        })

    out = {"meta": {"source": SOURCE, "count": len(shows)}, "shows": shows}
    (DATA / "netherlands.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {len(shows)} -> data/netherlands.json")

    coords = sum(1 for s in shows if s["lat"] is not None)
    print(f"kept={len(shows)} dropped={len(dropped)} coords={coords} null_coords={len(shows)-coords}")
    for d in dropped:
        print("  drop:", d)


if __name__ == "__main__":
    main()
