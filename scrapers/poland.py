"""Poland musicals — source: eBilet.pl (the dominant PL ticketing platform).

eBilet pages are server-rendered static HTML (no headless browser needed), but the
server rate-limits aggressive crawling (HTTP 429), so every request goes through a
polite throttle + exponential backoff.

How we read each show:
  - The "musicale" category page + per-city pages give us the set of event slugs:
      https://www.ebilet.pl/teatr/musicale
      https://www.ebilet.pl/teatr/musicale/miasto/{city}
  - Each event page (https://www.ebilet.pl/teatr/musicale/{slug}) carries:
      * a schema.org Event JSON-LD block (id="json-ld-event-data-...") with the clean
        title (name), venue (location.name), city (location.address.addressLocality)
        and a poster image. NOTE: the LD "image" URLs are corrupted by a doubled
        "https://www.ebilet.pl/media" prefix on eBilet's side, so we prefer og:image.
      * a JS data blob with "eventsDateFrom"/"eventsDateTo" = the authoritative run
        range, plus a list of "date":"YYYY-MM-DDT.." performance datetimes. We take
        the run from eventsDateFrom/To, falling back to min/max of future perf dates.

Non-musicals leak into the "musicale" bucket (concerts, recitals, galas, talent
shows, stand-up, solo-artist tours), so titles are filtered (see DROP/KEEP below).

Output: data/poland.json     Run: python scrapers/poland.py
"""

import json
import re
import sys
import io
import html
import time
import hashlib
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
DATA = Path(__file__).resolve().parent.parent / "data"
CET = timezone(timedelta(hours=2))  # Poland is CEST in summer; date-only comparisons
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0",
      "Accept-Language": "pl"}
BASE = "https://www.ebilet.pl"

# Cities eBilet exposes a musicale sub-page for. The category page is the real
# superset; the city pages just help surface any slug the category lazy-loads off.
CITIES = ["warszawa", "gdynia", "lodz", "wroclaw", "chorzow", "gliwice",
          "poznan", "krakow", "katowice", "gdansk", "bydgoszcz", "szczecin"]

# Building-level coordinates for the major Polish musical houses. Matched by
# case-insensitive substring against the venue name from the event page.
# (key substring) -> (lat, lng)
VENUES = {
    "roma":            (52.2247, 21.0156),  # Teatr Muzyczny ROMA, Nowogrodzka 49, Warszawa
    "syrena":          (52.2196, 21.0190),  # Teatr Syrena, Litewska 3, Warszawa
    "buffo":           (52.2270, 21.0260),  # Studio Buffo, Konopnickiej 6, Warszawa
    "gdyni":           (54.5167, 18.5360),  # Teatr Muzyczny w Gdyni, pl. Grunwaldzki 1
    "w łodzi":         (51.7800, 19.4690),  # Teatr Muzyczny w Łodzi, Północna 47/51
    "w lodzi":         (51.7800, 19.4690),
    "capitol":         (51.1015, 17.0265),  # Teatr Muzyczny Capitol, Piłsudskiego 67, Wrocław
    "rozrywki":        (50.2960, 18.9540),  # Teatr Rozrywki, Konopnickiej 1, Chorzów
    "gliwicki":        (50.2945, 18.6610),  # Gliwicki Teatr Muzyczny, Nowy Świat 55/57
    "w poznaniu":      (52.4030, 16.9230),  # Teatr Muzyczny w Poznaniu, Niezłomnych 1e
}

# --- Non-musical filter ----------------------------------------------------
# Drop if any of these substrings appear in the (lower-cased) title. Covers the
# concert / recital / gala / talent-show / stand-up / solo-artist-tour leakage.
DROP_WORDS = [
    "koncert", "recital", "jazz", "kolęd", "koled", "kabaret", "stand-up",
    "stand up", "komediowy", "komediowa", "gala", "talent show", " tour",
    "tribute", "symfonicz", "improwizowany", "improwizacja",
]
# Known solo artists whose "musicale"-bucket entries are live shows, not musicals.
DROP_ARTISTS = [
    "michał bajor", "michal bajor", "edyta geppert", "igor herbut",
    "grzegorz turnau", "kayah", "andrzej piaseczny",
]
# Strong KEEP signals — overrides the drop list (e.g. a title that contains both
# "musical" and a borderline word). Known musical/operetka titles + genre words.
KEEP_WORDS = [
    "musical", "musicalow", "operetka", "wicked", "six", "mamma mia",
    "skrzypek na dachu", "dracula", "beetlejuice", "madagaskar",
    "next to normal", "metro", "dzień świstaka", "dzien swistaka",
    "chłopi", "chlopi", "wiedźmin", "wiedzmin", "producenci", "high heels",
    "my fair lady", "polita",
]


def get(url, tries=6):
    """Fetch a URL as UTF-8 text, retrying with exponential backoff on 429/5xx.

    eBilet rate-limits bursts hard, so the backoff is generous (15s..90s)."""
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers=UA)
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read().decode("utf-8", "ignore")
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503) and k < tries - 1:
                time.sleep(15 * (k + 1))   # 15s, 30s, 45s, 60s, 75s
                continue
            return ""
        except Exception:
            if k < tries - 1:
                time.sleep(10 * (k + 1))
                continue
            return ""
    return ""


def collect_slugs():
    """Union of event slugs from the musicale category page + per-city pages."""
    slugs = {}
    pages = [f"{BASE}/teatr/musicale"] + \
            [f"{BASE}/teatr/musicale/miasto/{c}" for c in CITIES]
    for p in pages:
        d = get(p)
        for s in re.findall(r'href="/teatr/musicale/([^"/?#]+)"', d):
            slugs.setdefault(s, None)
        time.sleep(3.0)   # be polite between listing requests
    return list(slugs)


def is_musical(title):
    """Return (keep: bool, reason: str). KEEP words win over DROP words."""
    t = title.lower()
    if any(k in t for k in KEEP_WORDS):
        return True, "keep-signal"
    for a in DROP_ARTISTS:
        if a in t:
            return False, f"solo-artist ({a})"
    for w in DROP_WORDS:
        if w in t:
            return False, f"non-musical word ({w.strip()})"
    return None, "unsure"   # None = no strong signal either way


def parse_event(slug):
    """Fetch one event page → dict, or (None, reason) when it must be dropped."""
    url = f"{BASE}/teatr/musicale/{slug}"
    d = get(url)
    if not d:
        return None, f"{slug} (fetch failed)"

    # Clean title from og:title, fall back to the LD name.
    og_t = re.search(r'<meta property="og:title" content="([^"]+)"', d)
    title = html.unescape(og_t.group(1)).strip() if og_t else slug

    keep, reason = is_musical(title)
    if keep is False:
        return None, f"{title} ({reason})"

    # schema.org Event JSON-LD: venue + city (most reliable).
    venue = city = None
    m = re.search(r'<script type="application/ld\+json" id="json-ld-event-data[^"]*">(.*?)</script>',
                  d, re.S)
    if m:
        try:
            o = json.loads(m.group(1))
            if not title or title == slug:
                title = (o.get("name") or title).strip()
            loc = o.get("location") or {}
            venue = (loc.get("name") or "").strip() or None
            addr = loc.get("address") or {}
            city = (addr.get("addressLocality") or "").strip() or None
        except Exception:
            pass

    # If we still have no strong musical signal AND it's an unsure title, drop it
    # (instruction: "when unsure, exclude and log").
    if keep is None:
        return None, f"{title} (unsure — no musical signal)"

    # Run range: prefer the authoritative eventsDateFrom/To, else min/max of the
    # future performance dates ("date":"YYYY-MM-DD...").
    today = datetime.now(CET).strftime("%Y-%m-%d")
    ef = re.findall(r'"eventsDateFrom":"(20\d{2}-\d{2}-\d{2})', d)
    et = re.findall(r'"eventsDateTo":"(20\d{2}-\d{2}-\d{2})', d)
    perf = sorted(set(re.findall(r'"date":"(20\d{2}-\d{2}-\d{2})T', d)))
    future = [x for x in perf if x >= today]
    start = ef[0] if ef else (future[0] if future else None)
    end = et[0] if et else (future[-1] if future else None)
    if not start or not end:
        return None, f"{title} (no dates found)"
    # FUTURE/CURRENT only.
    if end < today:
        return None, f"{title} (ended {end})"

    # Poster: og:image is the clean URL (the LD image[] is corrupted by a doubled
    # /media prefix on eBilet's side).
    og_i = re.search(r'<meta property="og:image" content="([^"]+)"', d)
    image = og_i.group(1).strip() if og_i else None

    return {
        "title": title, "venue": venue, "city": city,
        "start": start, "end": end, "image": image, "url": url,
    }, "kept"


def venue_coords(venue):
    """Substring-match the venue name against VENUES → (lat, lng) or (None, None)."""
    if not venue:
        return None, None
    v = venue.lower()
    for key, (lat, lng) in VENUES.items():
        if key in v:
            return lat, lng
    return None, None


def main():
    slugs = collect_slugs()
    print(f"Found {len(slugs)} candidate slugs", flush=True)

    kept, dropped = [], []
    for slug in slugs:
        row, reason = parse_event(slug)
        if row is None:
            dropped.append(reason)
        else:
            kept.append(row)
        time.sleep(4.0)   # polite gap between event pages (avoids 429)

    shows = []
    coords_n = null_n = 0
    for s in kept:
        lat, lng = venue_coords(s["venue"])
        if lat is None:
            null_n += 1
        else:
            coords_n += 1
        sid = "pl-" + hashlib.md5(
            f"ebilet.pl|{s['title']}|{s['venue']}".encode()).hexdigest()[:8]
        shows.append({
            "id": sid, "title": s["title"], "title_en": "",
            "venue": s["venue"], "city": s["city"], "country": "Poland",
            "lat": lat, "lng": lng,
            "start_date": s["start"], "end_date": s["end"],
            "image": s["image"], "ticket_url": s["url"],
            "type": "tour", "verified": True, "source": "ebilet.pl",
        })

    out = {"meta": {"source": "ebilet.pl", "count": len(shows)}, "shows": shows}
    (DATA / "poland.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nWrote {len(shows)} -> data/poland.json", flush=True)
    print(f"  coords: {coords_n}   null-coords: {null_n}", flush=True)
    for s in shows:
        c = f"{s['lat']},{s['lng']}" if s["lat"] is not None else "no-coords"
        print(f"  keep: {s['title']} @ {s['venue']} ({s['city']}) "
              f"{s['start_date']}~{s['end_date']} [{c}]", flush=True)
    print(f"\nDropped {len(dropped)}:", flush=True)
    for d in dropped:
        print("  drop:", d, flush=True)


if __name__ == "__main__":
    main()
