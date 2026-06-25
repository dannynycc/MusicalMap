"""Spain-wide musicals — source: atrapalo.com (`/entradas/musicales/`).

atrapalo is the largest Spanish entertainment-ticketing site and the listing
pages embed a JSON-LD `ItemList` of `TheaterEvent` objects carrying everything
we need *already structured*: title, venue, **geo lat/lng** (so no geocoding),
full address (city/region/country), run dates, poster image and price. One
source therefore covers ALL of Spain — Madrid, Barcelona, Valencia, Sevilla,
Bilbao, Leganés … — with ~136 shows across 4 pages.

THE BOT WALL.  atrapalo sits behind Fastly's NextGen WAF "client challenge"
(`_fs-ch-…` / "Client Challenge" interstitial): a JS proof-of-work that mints a
clearance cookie `_fs_ch_cp_*` (1-hour TTL). A plain GET cannot solve it, so we
use a HYBRID model proven fastest:
  1. Playwright (real Chromium) loads page 1 once, runs the JS, passes the
     challenge, and we harvest the `_fs_ch_cp_*` cookie + page-1 JSON-LD.
  2. curl_cffi (Chrome TLS impersonation) reuses that cookie + the same UA to
     plain-GET the remaining pages fast — no browser per page.
The browser is just a ~3-second "lock-pick"; 99% of the fetch is light GET.

Spanish marketing titles are canonicalised via madrid.py's table so they merge
with the same show worldwide (Wicked, Les Misérables, Mamma Mia! …); local
Spanish productions keep their own name. build_shows dedups Madrid/Barcelona
overlaps with teatromadrid/barcelona by (show, city).

Output: data/atrapalo.json   Run: python scrapers/atrapalo.py
Needs: pip install curl_cffi playwright  (+ `playwright install chromium`).
       Scraper exits cleanly if a dependency is missing.
"""

import json
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from madrid import canon  # noqa: E402  (also sets UTF-8 stdout; shared ES→canonical table)

DATA = Path(__file__).resolve().parent.parent / "data"
BASE = "https://www.atrapalo.com/entradas/musicales/"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36")
MAX_PAGES = 12  # safety bound; we stop as soon as a page yields nothing new


def _page_url(n):
    return BASE if n == 1 else f"{BASE}p-{n}/"


def parse_ld_events(html):
    """Extract the TheaterEvent items from a listing page's JSON-LD ItemList."""
    events = []
    for blob in re.findall(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.S
    ):
        try:
            data = json.loads(blob.strip())
        except json.JSONDecodeError:
            continue
        for obj in data if isinstance(data, list) else [data]:
            if obj.get("@type") == "ItemList":
                for el in obj.get("itemListElement", []):
                    item = el.get("item")
                    if item:
                        events.append(item)
    return events


def fetch_pages():
    """Hybrid fetch: Playwright unlocks page 1, curl_cffi GETs the rest.

    Returns a de-duplicated list of raw TheaterEvent dicts (keyed by url)."""
    from playwright.sync_api import sync_playwright
    from curl_cffi import requests as creq

    by_url = {}
    with sync_playwright() as pw:
        browser = pw.chromium.launch(
            headless=True, args=["--disable-blink-features=AutomationControlled"]
        )
        ctx = browser.new_context(
            locale="es-ES", user_agent=UA, viewport={"width": 1366, "height": 900}
        )
        page = ctx.new_page()
        page.goto(_page_url(1), wait_until="domcontentloaded", timeout=45000)
        page.wait_for_selector('a[href*="_e"]', timeout=30000)  # past the reload
        time.sleep(1.0)
        for ev in parse_ld_events(page.content()):
            by_url.setdefault(ev.get("url"), ev)
        cookies = {}
        for c in ctx.cookies():
            n, v = c.get("name"), c.get("value")
            if n and v:
                cookies[n] = v
        browser.close()

    have_clearance = any(k.startswith("_fs_ch_cp_") for k in cookies)
    print(f"[atrapalo] page 1 via browser: {len(by_url)} events | "
          f"clearance cookie={'yes' if have_clearance else 'NO'}")

    sess = creq.Session(impersonate="chrome")
    for k, v in cookies.items():
        sess.cookies.set(k, v, domain=".atrapalo.com")
    headers = {"User-Agent": UA, "Accept-Language": "es-ES,es;q=0.9",
               "Referer": BASE}
    for n in range(2, MAX_PAGES + 1):
        r = sess.get(_page_url(n), headers=headers, timeout=30)
        if "Client Challenge" in r.text:
            print(f"[atrapalo] p-{n}: challenged — cookie expired/blocked, stop")
            break
        new = 0
        for ev in parse_ld_events(r.text):
            u = ev.get("url")
            if u and u not in by_url:
                by_url[u] = ev
                new += 1
        print(f"[atrapalo] p-{n} via GET: +{new} (total {len(by_url)})")
        if new == 0:
            break
        time.sleep(1.0)  # be gentle
    return list(by_url.values())


def clean_title(name_es):
    """Spanish marketing name → canonical title for cross-source merging.

    canon() (shared with madrid.py) only strips a *comma/period*-led
    ", el musical" suffix; atrapalo also uses a *dash* form ("Grease - El
    Musical") and trailing city tags. Strip the dash-suffix first so registry
    lookups hit (e.g. "Sonrisas y lágrimas - El musical" → The Sound of Music),
    then drop any dangling separator left behind."""
    base = re.sub(r'\s*[-–]\s*el\s+musical\s*$', '', name_es, flags=re.I).strip()
    title = canon(base)
    title = re.sub(r'\s*[-–,]\s*$', '', title).strip()
    return title or name_es


def to_show(ev):
    """Map one JSON-LD TheaterEvent to the MusicalMap show schema."""
    url = ev.get("url", "")
    m = re.search(r'/entradas/([a-z0-9-]+)_e\d+/?', url)
    slug = m.group(1) if m else None
    if not slug:
        return None
    loc = ev.get("location") or {}
    geo = loc.get("geo") or {}
    addr = loc.get("address") or {}
    offers = ev.get("offers") or []
    offer = (offers[0] if isinstance(offers, list) and offers
             else offers if isinstance(offers, dict) else {})

    lat, lng = geo.get("latitude"), geo.get("longitude")
    if lat is None or lng is None:
        return None  # no coords → cannot pin on the map; skip
    name_es = (ev.get("name") or "").strip()
    country = addr.get("addressCountry") or "España"
    country = "Spain" if country.strip().lower() in ("españa", "espana", "spain") else country

    show = {
        "id": f"atr-{slug}",
        "title": clean_title(name_es),           # registry canonical or cleaned original
        "type": "tour",                          # match madrid.py convention
        "venue": loc.get("name"),
        "city": addr.get("addressLocality") or addr.get("addressRegion"),
        "country": country,
        "lat": round(float(lat), 6),
        "lng": round(float(lng), 6),
        "start_date": ev.get("startDate"),
        "end_date": ev.get("endDate"),
        "ticket_url": url,
        "image": (ev.get("image") or "").split("?")[0] or None,
        "tour_name": name_es,                    # keep the Spanish marketing name
        "verified": True,
        "source": "atrapalo.com",
    }
    price = offer.get("price")
    if price:
        show["price_from"] = price
        show["currency"] = offer.get("priceCurrency", "EUR")
    return show


def main():
    try:
        raw = fetch_pages()
    except ImportError as e:
        print(f"[atrapalo] missing dependency ({e}); skipping.", file=sys.stderr)
        return
    shows, seen = [], set()
    for ev in raw:
        s = to_show(ev)
        if s and s["id"] not in seen:
            shows.append(s)
            seen.add(s["id"])
    shows.sort(key=lambda s: (s.get("city") or "", s.get("title") or ""))
    out = {"meta": {"source": "atrapalo.com", "count": len(shows)}, "shows": shows}
    path = DATA / "atrapalo.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    cities = sorted({s["city"] for s in shows if s.get("city")})
    print(f"[atrapalo] wrote {len(shows)} shows across {len(cities)} cities → {path.name}")
    print(f"[atrapalo] cities: {', '.join(cities)}")


if __name__ == "__main__":
    main()
