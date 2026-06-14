"""Middle East (Gulf) musicals — a concert/comedy-dominated region the global
scrapers miss entirely. Built source-by-source like the other regional scrapers.

  - Source: Platinumlist (dubai/abu-dhabi/qatar .platinumlist.net), the dominant
    Gulf ticketing site. Server-rendered static HTML.

  How it works (no API / no JSON-LD on this site):
    1. The /shows landing page tags every event card with a `data-ga4-click-item`
       JSON blob carrying the event id, title and CATEGORY ("type"). We keep only
       cards in "Theatrical Performances" + "Kids and Family Shows" (drop Comedy,
       Classical Music, Dance, Concerts/Popular).
    2. The Gulf is concert/comedy-heavy, so we FILTER HARD: a survivor is kept only
       if its title looks like a genuine staged musical (whitelist of known titles,
       or contains "musical"). Concerts, stand-up, galas, ice/aqua/dance shows,
       sports are dropped and logged.
    3. For each survivor we open the event detail page for the real venue + run
       dates. The live first show date comes from the booking `datetime=YYYY-MM-DD`
       param (year-anchored); the visible "buy-block__date-text" (e.g.
       "Sun 21 Jun - Thu 25 Jun") gives the run end (day+month, no year) which we
       year-anchor off the start (rolling the year if the end month wraps).

  Note on bot protection: the bare /shows URL 302-loops behind Queue-it. A plain
  CookieJar opener accepts the cookie and follows back to the real page — no
  headless browser needed.

Output: data/middleeast.json    Run: python scrapers/middleeast.py
"""

import json
import re
import sys
import io
import html
import hashlib
import urllib.request
import http.cookiejar
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
DATA = Path(__file__).resolve().parent.parent / "data"
GST = timezone(timedelta(hours=4))  # Gulf Standard Time
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
      "Accept-Language": "en-US,en;q=0.9",
      "Accept": "text/html,application/xhtml+xml"}

# One opener WITH a cookie jar per process: accepting the Queue-it cookie on the
# first request is what breaks the 302 redirect loop on the bare /shows page.
_CJ = http.cookiejar.CookieJar()
_OPENER = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(_CJ))

# Cities to scrape: (subdomain, default city label, country).
CITIES = [
    ("dubai",     "Dubai",     "United Arab Emirates"),
    ("abu-dhabi", "Abu Dhabi", "United Arab Emirates"),
    ("qatar",     "Doha",      "Qatar"),
]

# Only these landing-page categories can plausibly contain a staged musical.
KEEP_CATEGORIES = {"Theatrical Performances", "Kids and Family Shows", "Kids and Family"}

# Whitelist of known book musicals (substring, case-insensitive). A title also
# qualifies if it literally contains "musical".
MUSICAL_WHITELIST = [
    "wicked", "les miserables", "les misérables", "phantom", "mamma mia", "cats",
    "chicago", "grease", "mary poppins", "lion king", "aladdin", "frozen",
    "matilda", "charlie and the chocolate factory", "rumi", "annie",
    "jesus christ superstar", "evita", "hamilton", "sound of music", "six the",
    "school of rock", "beauty and the beast", "shrek", "elf the", "bodyguard",
    "dreamgirls", "rent the",
]

# HARD-exclude tokens: never a staged musical, drop even if the title also looks
# musical-ish (e.g. an opera/ice/dance/comedy show, a sports event).
HARD_EXCLUDE = [
    "stand-up", "standup", "comedy", "opera gala", "symphony", "orchestra",
    "riverdance", "taj express", "on ice", "la perle", " dj ", "ballet",
]
# SOFT-exclude tokens: typical of touring CONCERTS (artist + "Live"/"Tour"), but
# harmless on a genuine musical, so they only drop a title that has NO positive
# musical signal. e.g. "Chicago Musical ... Live" must survive; "Angham Live" must not.
SOFT_EXCLUDE = [" live", "tour", "concert", "festival"]

# Building-level coords, web-looked-up. Matched by case-insensitive substring of
# the scraped venue name; first match wins, so list more specific names first.
VENUES = {
    "dubai opera":                       (25.1936, 55.2735),
    "coca-cola arena":                   (25.1855, 55.2545),
    "etihad arena":                      (24.4672, 54.6033),  # Yas Island, Abu Dhabi
    "etihad park":                       (24.4699, 54.6010),  # Yas Island, Abu Dhabi
    "abu dhabi performing arts":         (24.4663, 54.3974),  # Saadiyat Cultural District
    "jumeirah beach hotel":              (25.1413, 55.1853),  # Meyana Theatre, JBH, Dubai
    "theatre by qe2":                    (25.2519, 55.2784),  # Queen Elizabeth 2, Mina Rashid
    "the junction":                      (25.1830, 55.2620),  # Alserkal Avenue, Al Quoz, Dubai
    "sima performing arts":              (25.1330, 55.2390),  # Al Quoz, Dubai
    "cultural foundation":               (24.4830, 54.3548),  # Cultural Foundation, Abu Dhabi
}


def get(url):
    """Fetch a page through the cookie-aware opener (handles the Queue-it loop)."""
    req = urllib.request.Request(url, headers=UA)
    with _OPENER.open(req, timeout=40) as r:
        return r.read().decode("utf-8", "ignore")


def og(d, key):
    """Pull an OpenGraph meta value (handles either attribute order)."""
    m = (re.search(r'property="' + key + r'"\s+content="([^"]+)"', d)
         or re.search(r'content="([^"]+)"\s+property="' + key + '"', d))
    return html.unescape(m.group(1)).strip() if m else None


def clean_show_title(t):
    """Strip Platinumlist marketing cruft so the title de-dups with the canonical
    work: '{Promoter} Presents …', '… Musical Event Live', '- The Musical',
    trailing 'in Dubai/Abu Dhabi/…', trailing year."""
    t = (t or "").strip()
    t = re.sub(r"^.{0,40}?\bpresents\b\s*:?\s+", "", t, flags=re.I)
    t = re.sub(r"\s*[-–]\s*(?:the\s+)?musical\b.*$", "", t, flags=re.I)
    t = re.sub(r"\s+musical event live\b.*$", "", t, flags=re.I)
    t = re.sub(r"\s+in\s+(?:dubai|abu\s*dhabi|doha|riyadh|sharjah|qatar)\b.*$", "", t, flags=re.I)
    t = re.sub(r"\s+20\d{2}\s*$", "", t)
    return t.strip(" ,-–")


def is_musical(title):
    """Hard filter: keep only genuine staged musicals; return (keep, reason)."""
    t = title.lower()
    # Hard excludes always win (opera/ice/dance/comedy/sports).
    for bad in HARD_EXCLUDE:
        if bad in t:
            return False, f"hard-excluded '{bad.strip()}'"
    # Positive signals: a whitelisted show name is STRONG; the bare word "musical"
    # is WEAK (galas/concerts also use it).
    named = next((w for w in MUSICAL_WHITELIST if w in t), None)
    if not named and "musical" not in t:
        return False, "not a known musical"
    # Concert tells (Live/Tour/Concert/Festival) drop a weak-only match, but a
    # whitelisted show name overrides them (e.g. "Chicago Musical ... Live").
    if not named:
        soft = next((s for s in SOFT_EXCLUDE if s in t), None)
        if soft:
            return False, f"weak match + concert tell '{soft.strip()}'"
        return True, "contains 'musical'"
    return True, f"whitelist '{named}'"


def parse_dates(d):
    """Return (start_date, end_date) as YYYY-MM-DD, or (None, None).

    start = the year-anchored booking `datetime=` param (earliest).
    end   = the day+month from buy-block__date-text, given the start's year and
            rolled forward a year if the end month wraps past the start.
    """
    starts = sorted(set(re.findall(r"datetime=(\d{4}-\d{2}-\d{2})", d)))
    if not starts:
        return None, None
    start = starts[0]
    sy, sm, sd = int(start[:4]), int(start[5:7]), int(start[8:10])
    end = start
    txt = re.search(r'buy-block__date-text[^>]*>([^<]+)<', d)
    if txt:
        # e.g. "Sun 21 Jun - Thu 25 Jun"  ->  end day=25 month=Jun
        parts = re.findall(r'(\d{1,2})\s+([A-Za-z]{3})', txt.group(1))
        if parts:
            ed, emon = parts[-1]
            months = {m: i for i, m in enumerate(
                ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                 "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}
            em = months.get(emon.title())
            if em:
                ey = sy + 1 if em < sm else sy  # run crosses into next year
                end = f"{ey:04d}-{em:02d}-{int(ed):02d}"
    return start, max(start, end)


def venue_coords(venue):
    if not venue:
        return None, None
    v = venue.lower()
    for key, (lat, lng) in VENUES.items():
        if key in v:
            return lat, lng
    return None, None


def scrape_city(sub, default_city, country, dropped):
    """Scrape one Platinumlist city subdomain. Returns kept rows."""
    base = f"https://{sub}.platinumlist.net"
    landing = get(base + "/shows")  # also warms the Queue-it cookie

    # Collect candidate event ids from the landing page, keeping only cards whose
    # GA4 category is Theatrical/Kids. {id: (title, category)}.
    cands = {}
    for raw in re.findall(r'data-ga4-click-item="([^"]+)"', landing):
        try:
            o = json.loads(html.unescape(raw))
        except Exception:
            continue
        if o.get("event_name") == "click_item" and o.get("item") == "event":
            if o.get("type") in KEEP_CATEGORIES and o.get("id") not in cands:
                cands[o["id"]] = (o.get("id_name") or "", o.get("type"))

    out = []
    today = datetime.now(GST).strftime("%Y-%m-%d")
    for eid, (title, cat) in cands.items():
        keep, reason = is_musical(title)
        if not keep:
            dropped.append(f"[{sub}/{cat}] {title} ({reason})")
            continue
        try:
            d = get(f"{base}/event/item/{eid}")
        except Exception as e:
            dropped.append(f"[{sub}] {title} (detail fetch failed: {e})")
            continue
        start, end = parse_dates(d)
        if not start:
            dropped.append(f"[{sub}] {title} (no bookable date)")
            continue
        end = end or start          # single-date shows: end defaults to start
        if end < today:
            dropped.append(f"[{sub}] {title} (past: ended {end})")
            continue
        vm = re.search(r'event-item__venue-name-text">([^<]+)<', d)
        venue = html.unescape(vm.group(1)).strip() if vm else None
        # Title: prefer the GA4 listing title; fall back to og:title; then strip the
        # Platinumlist marketing cruft ("X Presents …", "… Musical Event Live",
        # "- The Musical", trailing "in Dubai/Abu Dhabi", year) so it de-dups with
        # the canonical work ("Chicago Musical Event Live in Dubai" → "Chicago").
        clean = clean_show_title(title or (og(d, "og:title") or "").strip())
        url = og(d, "og:url") or f"{base}/event/item/{eid}"
        img = og(d, "og:image")
        out.append({
            "title": clean, "venue": venue or "", "city": default_city,
            "country": country, "start": start, "end": end,
            "image": img, "url": url,
        })
    print(f"  {sub}: {len(out)} kept (of {len(cands)} theatrical/kids candidates)", flush=True)
    return out


def main():
    rows, dropped = [], []
    for sub, city, country in CITIES:
        try:
            rows += scrape_city(sub, city, country, dropped)
        except Exception as e:
            print(f"  {sub} failed: {type(e).__name__}: {e}", flush=True)

    shows = []
    for s in rows:
        sid = "me-" + hashlib.md5(
            f"platinumlist|{s['title']}|{s['venue']}".encode()).hexdigest()[:8]
        lat, lng = venue_coords(s["venue"])
        shows.append({
            "id": sid, "title": s["title"], "title_en": "",
            "venue": s["venue"], "city": s["city"], "country": s["country"],
            "lat": lat, "lng": lng, "start_date": s["start"], "end_date": s["end"],
            "image": s["image"], "ticket_url": s["url"],
            "type": "tour", "verified": True, "source": "platinumlist",
        })

    out = {"meta": {"source": "platinumlist", "count": len(shows)}, "shows": shows}
    (DATA / "middleeast.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"\nWrote {len(shows)} -> data/middleeast.json", flush=True)
    coords = sum(1 for s in shows if s["lat"] is not None)
    print(f"coords: {coords} filled / {len(shows) - coords} null", flush=True)
    for s in shows:
        c = f"({s['lat']},{s['lng']})" if s["lat"] is not None else "(no coords)"
        print(f"  keep: {s['title']} @ {s['venue']} [{s['city']}] "
              f"{s['start_date']}~{s['end_date']} {c}", flush=True)
    print(f"\ndropped {len(dropped)}:", flush=True)
    for x in dropped:
        print("  drop:", x, flush=True)


if __name__ == "__main__":
    main()
