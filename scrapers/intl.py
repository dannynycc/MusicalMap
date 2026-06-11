"""International (non-US/UK) productions — source: broadway.org/broadway-shows-international

The page groups productions by country (<h2>Japan</h2> + a grid of cards). Each
card has the show title, venue, city, poster and official link, but NO dates —
these are open-ended sit-down productions, so we treat them as resident
(start/end = null → "currently playing"). The "London West End" group is skipped
(already covered by the West End scraper). Output: data/intl.json
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
URL = "https://www.broadway.org/broadway-shows-international"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MusicalMap/0.1"

# Famous venues Nominatim can't resolve by name (would otherwise all pile on the
# city centre). Matched by lowercase substring; verified real coordinates.
VENUE_COORDS = {
    "stage theater im hafen": (53.53989, 9.97325),    # Lion King, Hamburg
    "stage theater an der elbe": (53.53968, 9.97461),  # MJ, Hamburg (next door)
    "mehr! theater": (53.54277, 10.01669),             # Harry Potter, Hamburg
    "dentsu shiki": (35.66473, 139.7623),              # Aladdin, Tokyo
    "jr east shiki": (35.65369, 139.76294),            # Tokyo (Takeshiba)
    "tbs akasaka": (35.67287, 139.73517),              # Harry Potter, Tokyo
    "shiki theatre haru": (35.65511, 139.75706),       # Lion King, Tokyo
}

TITLE_RE = re.compile(r"<h4[^>]*>([^<]+)</h4>")
BOLD_RE = re.compile(r'<span class="bold">([^<]+)</span>')
IMG_RE = re.compile(r"background-image:\s*url\('([^']+)'")
HREF_RE = re.compile(r'href="([^"]+)"')


def main():
    req = urllib.request.Request(URL, headers={"User-Agent": UA})
    html = urllib.request.urlopen(req, timeout=30).read().decode("utf-8")
    parts = re.split(r"<h2>([^<]+)</h2>", html)

    shows = []
    for k in range(1, len(parts) - 1, 2):
        country = parts[k].strip()
        if "west end" in country.lower():   # already covered by westend.py
            continue
        body = parts[k + 1]
        items = re.findall(r'<div class="item">(.*?)(?=<div class="item">|<h2>|$)', body, re.S)
        for it in items:
            tm = TITLE_RE.search(it)
            if not tm:
                continue
            title = tm.group(1).strip()
            bolds = [b.strip() for b in BOLD_RE.findall(it)]
            venue = bolds[0] if bolds else country
            city = bolds[1] if len(bolds) > 1 else country
            img = IMG_RE.search(it)
            image = img.group(1).split("?")[0] if img else None
            href = HREF_RE.search(it)
            url = href.group(1) if href else URL

            mk = next((k for k in VENUE_COORDS if k in venue.lower()), None)
            if mk:
                lat, lng = VENUE_COORDS[mk]
            else:
                lat, lng = geocode(f"{venue}|{city}|{country}".lower(),
                                   f"{venue}, {city}, {country}")
                if lat is None:  # try venue without trailing qualifier, then city
                    lat, lng = geocode(f"{venue.split(',')[0]}|{city}|{country}".lower(),
                                       f"{venue.split(',')[0]}, {city}, {country}")
                if lat is None:
                    lat, lng = geocode(f"city|{city}|{country}".lower(), f"{city}, {country}")
            sid = re.sub(r"[^a-z0-9]+", "-", f"{title}-{city}".lower()).strip("-")
            shows.append({
                "id": f"intl-{sid}",
                "title": title,
                "type": "resident",
                "venue": venue,
                "city": city,
                "country": country,
                "lat": lat,
                "lng": lng,
                "start_date": None,
                "end_date": None,
                "ticket_url": url,
                "image": image,
                "tour_name": None,
                "verified": True,
                "source": "broadway.org/international",
            })
            print(f"  [{country}] {title} @ {venue}, {city}  ({lat},{lng})")

    out = {"meta": {"source": "broadway.org/international", "count": len(shows)}, "shows": shows}
    (DATA / "intl.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {len(shows)} international productions -> data/intl.json")


if __name__ == "__main__":
    main()
