"""Italian musicals — built in the same style as easteurope.py (stdlib only).

Source: teatro.it (statically scrapable with a browser User-Agent).

  - Genre listing: /spettacoli/genere/musical-varieta — a static HTML page that
    links to many /spettacoli/{slug} detail pages. We extract the unique show
    slugs (ignoring numeric ids, nav slugs like "genere"/"generi", and bare
    city slugs like "milano"/"roma").
  - Detail page: /spettacoli/{slug} — carries an application/ld+json block whose
    top object is usually an "EventSeries" (a tour). The series holds the show
    name + poster image; its subEvent[] array holds one "Event" per performance,
    each with location.name (venue), location.address.addressLocality (city),
    streetAddress, startDate and endDate. (A few pages expose a single "Event"
    with its own location instead of a series — both shapes are handled.)

Because teatro.it's "musical-varietà" bucket also leaks tribute/solo concerts,
stand-up comedians, opera/lirica, prose plays and drone shows, we run a keyword
KEEP/DROP filter (see is_musical) and log everything we drop.

Each show is emitted as ONE row (type:"tour"): the run spans the earliest future
performance to the latest future performance, and the primary venue/city is the
earliest future performance's location.

Output: data/italy.json     Run: python scrapers/italy.py
"""

import json
import re
import sys
import io
import html
import hashlib
import urllib.request
from datetime import datetime, timezone, timedelta
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
DATA = Path(__file__).resolve().parent.parent / "data"
CET = timezone(timedelta(hours=1))
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/124.0",
      "Accept-Language": "it"}
BASE = "https://www.teatro.it"
LISTING = BASE + "/spettacoli/genere/musical-varieta"

# ---------------------------------------------------------------------------
# Venue coords. The JSON-LD venue "name" is often a short form ("Brancaccio",
# "Arcimboldi", "Nazionale", "Sistina"), and the same short name can exist in
# more than one city, so we key on (venue-substring, city) and match
# case-insensitively. Coords are building-level, web-verified. Venues NOT here
# are left lat/lng = null for central geocoding (the address-derived city is
# still filled in correctly).
# ---------------------------------------------------------------------------
VENUES = {
    ("sistina", "roma"):     (41.904281, 12.486961),   # Teatro Sistina, Via Sistina 129
    ("brancaccio", "roma"):  (41.893555, 12.500885),   # Teatro Brancaccio, Via Merulana 244
    ("olimpico", "roma"):    (41.926425, 12.461236),   # Teatro Olimpico, Piazza Gentile da Fabriano 17
    ("nazionale", "milano"): (45.466777, 9.154037),    # Teatro Nazionale, Via Giordano Rota 1
    ("arcimboldi", "milano"):(45.514460, 9.213660),    # Teatro degli Arcimboldi, Viale dell'Innovazione 20
    ("geox", "padova"):      (45.417490, 11.856290),   # Gran Teatro Geox, Via G. Tassinari 1
    ("rossetti", "trieste"): (45.652370, 13.784510),   # Politeama Rossetti, Viale XX Settembre 45
}


def venue_coords(venue, city):
    """Substring + city match into VENUES → (lat, lng) or (None, None)."""
    v = (venue or "").lower()
    c = (city or "").lower()
    for (vk, ck), (lat, lng) in VENUES.items():
        if vk in v and ck in c:
            return lat, lng
    return None, None


def get(url):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", "ignore")


# ---------------------------------------------------------------------------
# Non-musical filter. teatro.it's musical-varietà bucket mixes in concerts,
# stand-up, opera and drone shows. KEEP wins over DROP: anything that clearly
# reads as a musical (or is a known title) is kept even if a DROP word also
# appears; otherwise DROP words exclude it. Unsure → exclude (and it's logged).
# ---------------------------------------------------------------------------
KNOWN_MUSICALS = [
    "notre dame de paris", "moulin rouge", "cats", "mamma mia", "cenerentola",
    "aggiungi un posto a tavola", "forza venite gente", "frida", "gloria",
    "scugnizzi", "amelie", "amélie", "principe d'egitto", "principe degitto",
    "we will rock you", "flashdance", "tootsie", "anastasia", "matilda",
    "grease", "febbre del sabato sera", "divina commedia", "pinocchio",
    "peter pan", "mrs doubtfire", "mrs. doubtfire", "a christmas carol",
    "oceania", "lupin", "alice nel paese delle meraviglie", "win for life",
    "ragazzo dai pantaloni rosi", "ragazzo dai pantaloni rosa",
]
KEEP_WORDS = ["musical", "il musical", "opera musical"]
# Solo-artist / concert / stand-up / opera / prose / drone / gala markers.
DROP_WORDS = [
    " live", "live ", " in concerto", "concerto", " tour", "tour ",
    "omaggio", "tributo", "tribute", "stand up", "stand-up", "comici",
    "droneart", "drone", "gala", "galà", "balletto", "danza",
    "sinfonic", "orchestra", "recital", "one man show", "one-man",
]
# Known non-musical solo acts / comedians frequently in this bucket.
DROP_NAMES = [
    "enrico brignano", "max giusti", "paolo ruffini", "roberto bolle",
    "arisa", "raffaella", "win for life", "oblivion", "theodoros terzopoulos",
    "le baccanti", "the jury experience", "maradona", "michelangelo",
    "23 ore e mezza", "giorgio marchesi",
]


def is_musical(title, slug):
    """Return (keep: bool, reason: str)."""
    t = (title or "").lower()
    s = (slug or "").lower()
    blob = t + " " + s.replace("-", " ")
    # KEEP: explicit "musical" or a known title wins outright.
    if any(k in blob for k in KEEP_WORDS):
        return True, "musical-keyword"
    if any(k in blob for k in KNOWN_MUSICALS):
        return True, "known-musical"
    # DROP: solo names / concert / opera / drone markers.
    for n in DROP_NAMES:
        if n in blob:
            return False, f"non-musical name ({n})"
    for w in DROP_WORDS:
        if w in blob:
            return False, f"non-musical keyword ({w.strip()})"
    # Unsure → exclude (logged by caller).
    return False, "unsure (no musical marker)"


def parse_event_blocks(d):
    """Yield every Event/EventSeries-shaped dict in the page's ld+json blocks,
    flattening @graph and lists. Returns dicts that look like events
    (have startDate or @type Event/EventSeries)."""
    out = []
    for raw in re.findall(
            r'<script[^>]*type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
            d, re.S):
        try:
            j = json.loads(raw)
        except Exception:
            continue
        stack = j if isinstance(j, list) else [j]
        while stack:
            it = stack.pop()
            if not isinstance(it, dict):
                continue
            if isinstance(it.get("@graph"), list):
                stack.extend(it["@graph"])
            t = it.get("@type")
            if t in ("Event", "EventSeries") or it.get("startDate"):
                out.append(it)
    return out


def loc_fields(ev):
    """Pull (venue, city) from an event's location.{name,address.locality}."""
    loc = ev.get("location")
    if isinstance(loc, list):
        loc = loc[0] if loc else None
    if not isinstance(loc, dict):
        return None, None
    venue = loc.get("name")
    addr = loc.get("address") or {}
    if isinstance(addr, list):
        addr = addr[0] if addr else {}
    city = addr.get("addressLocality") if isinstance(addr, dict) else None
    return (venue.strip() if venue else None), (city.strip() if city else None)


def first_image(ev):
    img = ev.get("image")
    if isinstance(img, list):
        return img[0] if img else None
    return img


def scrape():
    lst = get(LISTING)
    # Unique show slugs; drop numeric ids, nav slugs and bare city slugs.
    nav = {"genere", "generi"}
    cities = {"milano", "roma", "bari", "napoli", "torino", "bologna",
              "firenze", "genova", "palermo", "venezia", "verona", "padova",
              "trieste", "catania", "brescia", "bergamo"}
    slugs = []
    for s in dict.fromkeys(re.findall(r"/spettacoli/([a-z0-9][a-z0-9-]+)", lst)):
        if s in nav or s in cities or s.isdigit():
            continue
        slugs.append(s)

    today = datetime.now(CET).strftime("%Y-%m-%d")
    out, dropped, seen = [], [], set()

    for slug in slugs:
        url = f"{BASE}/spettacoli/{slug}"
        try:
            d = get(url)
        except Exception as e:
            dropped.append(f"{slug} (fetch failed: {e})")
            continue

        events = parse_event_blocks(d)
        if not events:
            dropped.append(f"{slug} (no ld+json event)")
            continue

        # Title: prefer the series-level name, else any event name.
        series = next((e for e in events if e.get("@type") == "EventSeries"), None)
        head = series or events[0]
        title = html.unescape((head.get("name") or slug).strip())

        keep, reason = is_musical(title, slug)
        if not keep:
            dropped.append(f"{title} [{slug}] — {reason}")
            continue

        # Gather candidate performances: subEvents if present, else the events.
        perfs = []
        for e in events:
            sub = e.get("subEvent")
            if isinstance(sub, list):
                perfs.extend(x for x in sub if isinstance(x, dict))
            elif e.get("startDate"):
                perfs.append(e)
        if not perfs:
            dropped.append(f"{title} [{slug}] — no performances")
            continue

        # Keep only future/current performances (end_date >= today).
        future = []
        for p in perfs:
            sd = (p.get("startDate") or "")[:10]
            ed = (p.get("endDate") or sd)[:10]
            if not re.match(r"20\d{2}-\d{2}-\d{2}", sd):
                continue
            if ed and ed[:10] >= today:
                venue, city = loc_fields(p)
                future.append((sd, ed[:10], venue, city))
        if not future:
            dropped.append(f"{title} [{slug}] — already ended / no future dates")
            continue

        future.sort(key=lambda x: x[0])
        start = future[0][0]
        end = max(x[1] for x in future)
        venue = future[0][2]               # primary = earliest future stop
        city = future[0][3]
        # Fall back to series-level location if the subEvent had none.
        if not venue:
            venue, scity = loc_fields(head)
            city = city or scity
        if not venue:
            dropped.append(f"{title} [{slug}] — no venue")
            continue

        key = (title.lower(), (venue or "").lower())
        if key in seen:
            continue
        seen.add(key)

        out.append({
            "title": title, "venue": venue, "city": city or "",
            "start": start, "end": end,
            "image": first_image(head) or first_image(future and perfs[0]),
            "url": url,
        })
    return out, dropped


def main():
    rows, dropped = scrape()
    shows = []
    n_coords = 0
    for s in rows:
        lat, lng = venue_coords(s["venue"], s["city"])
        if lat is not None:
            n_coords += 1
        sid = "it-" + hashlib.md5(
            f"teatro.it|{s['title']}|{s['venue']}".encode()).hexdigest()[:8]
        shows.append({
            "id": sid, "title": s["title"], "title_en": "",
            "venue": s["venue"], "city": s["city"], "country": "Italy",
            "lat": lat, "lng": lng,
            "start_date": s["start"], "end_date": s["end"],
            "image": s["image"], "ticket_url": s["url"],
            "type": "tour", "verified": True, "source": "teatro.it",
        })

    out = {"meta": {"source": "teatro.it", "count": len(shows)}, "shows": shows}
    (DATA / "italy.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Wrote {len(shows)} -> data/italy.json "
          f"({n_coords} with coords, {len(shows) - n_coords} null)", flush=True)
    for s in shows:
        c = "" if s["lat"] is None else " [coords]"
        print(f"    keep: {s['title']} @ {s['venue']} ({s['city']}) "
              f"{s['start_date']}~{s['end_date']}{c}", flush=True)
    print(f"  dropped {len(dropped)}:", flush=True)
    for d in dropped:
        print("    drop:", d, flush=True)


if __name__ == "__main__":
    main()
