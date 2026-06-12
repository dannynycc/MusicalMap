"""ATG Tickets (UK regional circuit) — source: atgtickets.com/whats-on/uk/musicals/

No public API (the GraphQL endpoint is customer-profile only); the listing is
server-rendered MUI cards, paginated via ?page=N. Each single-venue card gives
title / venue / date text ("Until Sat 13 Jun 2026" or "Fri 12 Jun 2026 - Sun 7
Mar 2027") / image / link. Venue city is read from the venue slug suffix when
it names a UK city (theatre-royal-glasgow), else geocoded (cached).

"Tour (N Venues)" cards need a per-venue hub crawl — NOT covered yet (phase 2,
recorded in docs/SOURCES.md); big UK tours are covered via manual.json.

Output: data/atg.json   Run: python scrapers/atg.py
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
BASE = "https://www.atgtickets.com"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MusicalMap/0.1"
MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], 1)}
UK_CITIES = ["london", "glasgow", "edinburgh", "manchester", "liverpool", "birmingham",
             "leeds", "bristol", "cardiff", "swansea", "woking", "brighton", "oxford",
             "milton-keynes", "stockton", "sunderland", "york", "hull", "sheffield",
             "nottingham", "leicester", "southampton", "portsmouth", "plymouth",
             "torquay", "wimbledon", "richmond", "bromley", "dartford", "aylesbury",
             "glynde", "folkestone"]


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "ignore")


def parse_date(s):
    m = re.search(r"(\d{1,2})\s+([A-Za-z]{3})\w*\s+(\d{4})", s)
    if not m:
        return None
    d, mon, y = m.groups()
    mn = MONTHS.get(mon[:3].title())
    return f"{y}-{mn:02d}-{int(d):02d}" if mn else None


def card_records(html):
    for c in re.findall(r'data-testid="showCard"(.*?)(?=data-testid="showCard"|</main|$)', html, re.S):
        href = re.search(r'href="(/shows/[^"]+)"', c)
        img = re.search(r'srcSet="(https://[^"\s]+?)(?:\s|")', c)
        text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "|", c))
        parts = [p.strip() for p in text.split("|") if p.strip() and "Paper-shadow" not in p]
        if not href or not parts:
            continue
        title = parts[0]
        if re.search(r"Tour \(\d+ Venues?\)", text):
            yield {"tour_card": True, "title": title}
            continue
        venue = None
        for p in parts:
            if p == title or p.startswith(("Musicals", "Buy tickets", "More info")):
                continue
            if re.match(r"(Until|From|\w{3}\s+\d)", p):
                continue
            venue = p
            break
        dm = re.search(r"(Until\s+[^|]+?\d{4})|((?:\w{3}\s+)?\d{1,2}\s+\w{3}\s+\d{4}\s*[-–]\s*(?:\w{3}\s+)?\d{1,2}\s+\w{3}\s+\d{4})", text)
        start = end = None
        if dm:
            seg = dm.group(0)
            if seg.startswith("Until"):
                end = parse_date(seg)
            else:
                halves = re.split(r"[-–]", seg)
                start, end = parse_date(halves[0]), parse_date(halves[1])
        yield {"tour_card": False, "title": title, "href": href.group(1),
               "image": img.group(1) if img else None, "venue": venue,
               "start": start, "end": end}


def clean_title(t):
    # promoter prefixes ("TSP presents …", "BMOS presents …") and Disney brand
    t = re.sub(r"^[A-Za-z&.\' ]{2,40}\bpresents\s+", "", t, flags=re.I)
    t = re.sub(r"^disney'?s\s+", "", t, flags=re.I)
    return t.strip()


def main():
    shows, tour_cards = {}, []
    for page in range(1, 8):
        html = fetch(f"{BASE}/whats-on/uk/musicals/?page={page}")
        got = list(card_records(html))
        if not any(not r["tour_card"] for r in got) and page > 1:
            break
        for r in got:
            if r["tour_card"]:
                tour_cards.append(r["title"])
                continue
            import html as _h
            title = _h.unescape(clean_title(r["title"]))
            venue = r["venue"] or ""
            vslug = r["href"].rstrip("/").split("/")[-1]
            city = next((c.title().replace("-", " ") for c in UK_CITIES
                         if vslug.endswith("-" + c) or vslug == c), None)
            if city is None and "london" not in vslug:
                # London venues have no suffix; assume London only for known West End slugs
                city = "London" if re.search(r"savoy|lyceum|playhouse|apollo-victoria|dominion|fortune|duke-of-york|harold-pinter|phoenix|piccadilly|trafalgar|ambassadors", vslug) else None
            lat = lng = None
            q_city = city or "UK"
            if r["start"] is None and r["end"] is None:
                continue  # dates are JS-only on detail pages — never show undated as "playing now"
            lat, lng = geocode(f"{vslug}|uk", f"{venue}, {q_city}, UK")
            if lat is None:
                continue  # never guess
            sid = "atg-" + re.sub(r"[^a-z0-9]+", "-", r["href"].lower()).strip("-")
            shows[sid] = {
                "id": sid, "title": title, "type": "tour",
                "venue": venue, "city": city or venue, "country": "UK",
                "lat": lat, "lng": lng,
                "start_date": r["start"], "end_date": r["end"],
                "ticket_url": BASE + r["href"],
                "image": r["image"], "tour_name": None,
                "verified": True, "source": "atgtickets.com",
            }
            print(f"  {title[:30]:32s} @ {venue[:28]:30s} {r['start']} – {r['end']}")

    out = {"meta": {"source": "atgtickets.com", "count": len(shows),
                    "tour_cards_not_covered": sorted(set(tour_cards))}, "shows": list(shows.values())}
    (DATA / "atg.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nWrote {len(shows)} shows -> data/atg.json")
    if tour_cards:
        print(f"⚠ tour cards (per-venue crawl = phase 2): {sorted(set(tour_cards))}")


if __name__ == "__main__":
    main()
